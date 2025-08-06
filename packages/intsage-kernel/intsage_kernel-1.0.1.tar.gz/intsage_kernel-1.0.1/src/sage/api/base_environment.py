from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
import os
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Type, Union, Any
from sage.api.function.lambda_function import wrap_lambda
from sage.api.datastream import DataStream
from sage.kernels.core.transformation.base_transformation import BaseTransformation
from sage.kernels.core.transformation.source_transformation import SourceTransformation
from sage.kernels.core.transformation.batch_transformation import BatchTransformation
from sage.kernels.core.transformation.future_transformation import FutureTransformation
from sage.kernels.runtime.communication.queue_descriptor.base_queue_descriptor import BaseQueueDescriptor
from sage.utils.logging.custom_logger import CustomLogger
from sage.kernels.jobmanager.utils.name_server import get_name
from sage.kernels.jobmanager.jobmanager_client import JobManagerClient
from sage.kernels.runtime.factory.service_factory import ServiceFactory
if TYPE_CHECKING:
    from sage.kernels.jobmanager.job_manager import JobManager
    from sage.api.function.base_function import BaseFunction

    
class BaseEnvironment(ABC):

    __state_exclude__ = ["_engine_client", "client", "jobmanager"]
    # 会被继承，但是不会被自动合并

    def __init__(self, name: str, config: dict | None, *, platform: str = "local"):

        self.name = get_name(name)
        self.uuid: Optional[str] # 由jobmanager生成

        self.config: dict = dict(config or {})
        self.platform:str = platform
        # 用于收集所有 BaseTransformation，供 ExecutionGraph 构建 DAG
        self.pipeline: List[BaseTransformation] = []
        self._filled_futures: dict = {}  
        # 用于收集所有服务工厂，供任务提交时生成服务任务
        self.service_factories: dict = {}  # service_name -> ServiceFactory
        self.service_task_factories: dict = {}  # service_name -> ServiceTaskFactory

        self.env_base_dir: Optional[str] = None  # 环境基础目录，用于存储日志和其他文件
        # JobManager 相关
        self._jobmanager: Optional[Any] = None
        
        # Engine 客户端相关
        self._engine_client: Optional[JobManagerClient] = None
        self.env_uuid: Optional[str] = None
        
        # 日志配置
        self.console_log_level: str = "INFO"  # 默认console日志等级

    ########################################################
    #                  user interface                      #
    ########################################################

    def set_console_log_level(self, level: str):
        """
        设置控制台日志等级
        
        Args:
            level: 日志等级，可选值: "DEBUG", "INFO", "WARNING", "ERROR"
            
        Example:
            env.set_console_log_level("DEBUG")  # 显示所有日志
            env.set_console_log_level("WARNING")  # 只显示警告和错误
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
        
        self.console_log_level = level.upper()
        
        # 如果logger已经初始化，更新其配置
        if hasattr(self, '_logger') and self._logger is not None:
            self._logger.update_output_level("console", self.console_log_level)


    def register_service(self, service_name: str, service_class: Type, *args, **kwargs):
        """
        注册服务到环境中
        
        Args:
            service_name: 服务名称，用于标识服务
            service_class: 服务类，将在任务提交时实例化
            *args: 传递给服务构造函数的位置参数
            **kwargs: 传递给服务构造函数的关键字参数
            
        Example:
            # 注册一个自定义服务
            env.register_service("my_cache", MyCacheService, cache_size=1000)
            
            # 注册数据库连接服务
            env.register_service("db_conn", DatabaseConnection, 
                               host="localhost", port=5432, db="mydb")
        """
        # 创建服务工厂
        service_factory = ServiceFactory(
            service_name=service_name,
            service_class=service_class,
            service_args=args,
            service_kwargs=kwargs
        )
        
        # 创建服务任务工厂
        from sage.kernels.runtime.factory.service_task_factory import ServiceTaskFactory
        service_task_factory = ServiceTaskFactory(
            service_factory=service_factory,
            remote=(self.platform == "remote")
        )
        
        self.service_factories[service_name] = service_factory
        self.service_task_factories[service_name] = service_task_factory
        
        platform_str = "remote" if self.platform == "remote" else "local"
        self.logger.info(f"Registered {platform_str} service: {service_name} ({service_class.__name__})")
        
        return service_factory

    def from_kafka_source(self, 
                         bootstrap_servers: str,
                         topic: str,
                         group_id: str,
                         auto_offset_reset: str = 'latest',
                         value_deserializer: str = 'json',
                         buffer_size: int = 10000,
                         max_poll_records: int = 500,
                         **kafka_config) -> DataStream:
        """
        创建Kafka数据源，采用Flink兼容的架构设计
        
        Args:
            bootstrap_servers: Kafka集群地址 (例: "localhost:9092")
            topic: Kafka主题名称
            group_id: 消费者组ID，用于offset管理
            auto_offset_reset: offset重置策略 ('latest'/'earliest'/'none')
            value_deserializer: 反序列化方式 ('json'/'string'/'bytes'或自定义函数)
            buffer_size: 本地缓冲区大小，防止数据丢失
            max_poll_records: 每次poll的最大记录数，控制批处理大小
            **kafka_config: 其他Kafka Consumer配置参数
            
        Returns:
            DataStream: 可用于构建处理pipeline的数据流
            
        Example:
            # 基本使用
            kafka_stream = env.from_kafka_source(
                bootstrap_servers="localhost:9092",
                topic="user_events", 
                group_id="sage_consumer"
            )
            
            # 高级配置
            kafka_stream = env.from_kafka_source(
                bootstrap_servers="kafka1:9092,kafka2:9092",
                topic="events",
                group_id="sage_app",
                auto_offset_reset="earliest",
                buffer_size=20000,
                max_poll_records=1000,
                session_timeout_ms=30000,
                security_protocol="SSL"
            )
            
            # 构建处理pipeline
            result = (kafka_stream
                     .map(ProcessEventFunction)
                     .filter(FilterFunction)
                     .sink(OutputSinkFunction))
        """
        from sage.api.function.kafka_source import KafkaSourceFunction
        
        # 创建Kafka Source Function
        transformation = SourceTransformation(
            self,
            KafkaSourceFunction,
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            value_deserializer=value_deserializer,
            buffer_size=buffer_size,
            max_poll_records=max_poll_records,
            **kafka_config
        )
        
        self.pipeline.append(transformation)
        self.logger.info(f"Kafka source created for topic: {topic}, group: {group_id}")
        
        return DataStream(self, transformation)

    def from_source(self, function: Union[Type['BaseFunction'], callable], *args, **kwargs) -> DataStream:
        if callable(function) and not isinstance(function, type):
            # 这是一个 lambda 函数或普通函数
            function = wrap_lambda(function, 'flatmap')
        transformation = SourceTransformation(self, function, *args, **kwargs)

        self.pipeline.append(transformation)
        return DataStream(self, transformation)



    def from_collection(self, function: Union[Type['BaseFunction'], callable], *args, **kwargs) -> DataStream:
        if callable(function) and not isinstance(function, type):
            # 这是一个 lambda 函数或普通函数
            function = wrap_lambda(function, 'flatmap')
        transformation = BatchTransformation(self, function, *args,
                                              **kwargs)  # TODO: add a new transformation 去告诉engine这个input source是有界的，当执行完毕之后，会发送一个endofinput信号来停止所有进程。
                                                         # Issue URL: https://github.com/intellistream/SAGE/issues/387

        self.pipeline.append(transformation)
        return DataStream(self, transformation)

    def from_batch(self, source: Union[Type['BaseFunction'], Any], *args, **kwargs) -> DataStream:
        """
        统一的批处理数据源创建方法，支持多种输入类型
        
        Args:
            source: 可以是以下类型之一：
                   - BaseFunction 子类：自定义批处理函数类
                   - list/tuple：数据列表或元组
                   - 任何可迭代对象：实现了 __iter__ 的对象
            *args: 传递给批处理函数的位置参数（仅当 source 为函数类时有效）
            **kwargs: 传递给批处理函数的关键字参数，以及 transformation 的配置参数
            
        Returns:
            DataStream: 包含 BatchTransformation 的数据流
            
        Example:
            # 1. 使用自定义批处理函数类
            class MyBatchFunction(BaseFunction):
                def get_data_iterator(self):
                    return iter(range(50))
                    
                def get_total_count(self):
                    return 50
            
            batch_stream = env.from_batch(MyBatchFunction, custom_param="value")
            
            # 2. 使用数据列表
            data = ["item1", "item2", "item3", "item4", "item5"]
            batch_stream = env.from_batch(data)
            
            # 3. 使用任何可迭代对象
            batch_stream = env.from_batch({1, 2, 3, 4, 5})
            batch_stream = env.from_batch("hello")  # 逐字符迭代
            batch_stream = env.from_batch(range(100))
            
            # 4. 配置额外参数
            batch_stream = env.from_batch(data, progress_log_interval=10)
        """
        
        # 检查 source 的类型并相应处理
        if isinstance(source, type) and hasattr(source, '__bases__'):
            # source 是一个类，检查是否是 BaseFunction 的子类
            from sage.api.function.base_function import BaseFunction
            if issubclass(source, BaseFunction):
                # 使用自定义批处理函数类
                return self._from_batch_function_class(source, *args, **kwargs)
        
        # source 是数据对象，需要检查其类型
        if isinstance(source, (list, tuple)):
            # 处理列表或元组
            return self._from_batch_collection(source, **kwargs)
        elif hasattr(source, '__iter__') and not isinstance(source, (str, bytes)):
            # 处理其他可迭代对象（排除字符串和字节）
            return self._from_batch_iterable(source, **kwargs)
        elif isinstance(source, (str, bytes)):
            # 特殊处理字符串和字节，按字符/字节迭代
            return self._from_batch_iterable(source, **kwargs)
        else:
            # 尝试将其作为可迭代对象处理
            try:
                iter(source)
                return self._from_batch_iterable(source, **kwargs)
            except TypeError:
                raise TypeError(
                    f"Unsupported source type: {type(source)}. "
                    f"Expected BaseFunction subclass, list, tuple, or any iterable object."
                )




    def from_future(self, name: str) -> DataStream:
        """
        创建一个future stream占位符，用于建立反馈边。
        
        Args:
            name: future stream的名称，用于标识和调试
            
        Returns:
            DataStream: 包含FutureTransformation的数据流
            
        Example:
            future_stream = env.from_future("feedback_loop")
            # 使用future_stream参与pipeline构建
            result = source.connect(future_stream).comap(CombineFunction)
            # 最后填充future
            result.fill_future(future_stream)
        """
        transformation = FutureTransformation(self, name)
        self.pipeline.append(transformation)
        return DataStream(self, transformation)

    ########################################################
    #                jobmanager interface                  #
    ########################################################
    @abstractmethod
    def submit(self):
        pass


    ########################################################
    #                properties                            #
    ########################################################

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = CustomLogger()
        return self._logger

    @property
    def client(self)-> JobManagerClient:
        if self._engine_client is None:
            # 从配置中获取 Engine 地址，或使用默认值
            daemon_host = self.config.get("engine_host", "127.0.0.1")
            daemon_port = self.config.get("engine_port", 19000)
            
            self._engine_client = JobManagerClient(host=daemon_host, port=daemon_port)
            
        return self._engine_client






    ########################################################
    #                called inside methods                 #
    ########################################################

    def setup_logging_system(self, log_base_dir: str): 
        self.name = get_name(self.name)
        # 这行代码的目的是让自己在jobmanager的名字唯一，不与其他注册过的环境冲突
        # this method is called by jobmanager when receiving the job, not the user
        self.session_timestamp = datetime.now()
        self.session_id = self.session_timestamp.strftime("%Y%m%d_%H%M%S")
        # self.log_base_dir = log_base_dir
        self.env_base_dir = os.path.join(log_base_dir, f"env_{self.name}_{self.session_id}")
        Path(self.env_base_dir).mkdir(parents=True, exist_ok=True)

        self._logger = CustomLogger([
                ("console", self.console_log_level),  # 使用用户设置的控制台日志等级
                (os.path.join(self.env_base_dir, "Environment.log"), "DEBUG"),  # 详细日志
                (os.path.join(self.env_base_dir, "Error.log"), "ERROR")  # 错误日志
            ],
            name = f"Environment_{self.name}",
        )
    
    @abstractmethod
    @abstractmethod
    def get_qd(self, name: str, maxsize: int = 10000) -> 'BaseQueueDescriptor':
        """
        创建队列描述符
        
        Args:
            name: 队列名称/ID
            maxsize: 队列最大容量
            
        Returns:
            队列描述符实例
        """
        pass
    

    ########################################################
    #                auxiliary methods                     #
    ########################################################

    def _append(self, transformation: BaseTransformation):
        """将 BaseTransformation 添加到管道中（Compiler 会使用）。"""
        self.pipeline.append(transformation)
        return DataStream(self, transformation)

    def _from_batch_function_class(self, batch_function_class: Type['BaseFunction'], *args, **kwargs) -> DataStream:
        """
        从自定义批处理函数类创建批处理数据源
        """
        # 分离transformation配置和function参数
        transform_kwargs = {}
        function_kwargs = {}
        
        # transformation相关的参数
        transform_config_keys = {'delay', 'progress_log_interval'}
        
        for key, value in kwargs.items():
            if key in transform_config_keys:
                transform_kwargs[key] = value
            else:
                function_kwargs[key] = value
        
        transformation = BatchTransformation(
            self,
            batch_function_class,
            *args,
            **function_kwargs,
            **transform_kwargs
        )
        
        self.pipeline.append(transformation)
        self.logger.info(f"Custom batch source created with {batch_function_class.__name__}")
        
        return DataStream(self, transformation)

    def _from_batch_collection(self, data: Union[list, tuple], **kwargs) -> DataStream:
        """
        从数据集合创建批处理数据源
        """
        from sage.api.function.simple_batch_function import SimpleBatchIteratorFunction
        
        transformation = BatchTransformation(
            self,
            SimpleBatchIteratorFunction,
            data=data,
            **kwargs
        )
        
        self.pipeline.append(transformation)
        self.logger.info(f"Batch collection source created with {len(data)} items")
        
        return DataStream(self, transformation)

    def _from_batch_iterable(self, iterable: Any, **kwargs) -> DataStream:
        """
        从任何可迭代对象创建批处理数据源
        """
        from sage.api.function.simple_batch_function import IterableBatchIteratorFunction
        
        # 尝试获取总数量
        total_count = kwargs.pop('total_count', None)
        if total_count is None:
            try:
                total_count = len(iterable)
            except TypeError:
                # 如果对象没有 len() 方法，则保持 None
                total_count = None
        
        transformation = BatchTransformation(
            self,
            IterableBatchIteratorFunction,
            iterable=iterable,
            total_count=total_count,
            **kwargs
        )
        
        self.pipeline.append(transformation)
        
        # 构建日志信息
        type_name = type(iterable).__name__
        count_info = f" with {total_count} items" if total_count is not None else ""
        self.logger.info(f"Batch iterable source created from {type_name}{count_info}")
        
        return DataStream(self, transformation)