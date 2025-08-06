import os
from abc import ABC, abstractmethod
from typing import Type, List, Tuple, Any, TYPE_CHECKING, Union
from sage.kernels.runtime.service.service_caller import ServiceManager, ServiceCallProxy
if TYPE_CHECKING:
    from sage.kernels.runtime.task_context import TaskContext
    from sage.kernels.runtime.service.service_caller import ServiceManager
import logging
from sage.kernels.runtime.state import load_function_state, save_function_state


# 构造来源于sage.kernels.runtime/operator/factory.py
class BaseFunction(ABC):
    """
    BaseFunction is the abstract base class for all operator functions in SAGE.
    It defines the core interface and initializes a logger.
    """
    def __init__(self, *args, **kwargs):
        self.ctx: 'TaskContext' = None # 运行时注入
        self.router = None  # 运行时注入
        self._logger = None
        # 服务代理缓存
        self._call_service_proxy = None
        self._call_service_async_proxy = None

    @property
    def logger(self):
        if not hasattr(self, "_logger") or self._logger is None:
            if self.ctx is None:
                self._logger = logging.getLogger("")
            else:
                self._logger = self.ctx.logger
        return self._logger
    
    @property
    def name(self):
        return self.ctx.name
    
    @property
    def call_service(self):
        """
        同步服务调用语法糖
        
        用法:
            result = self.call_service["cache_service"].get("key1")
            data = self.call_service["db_service"].query("SELECT * FROM users")
        """
        if self.ctx is None:
            raise RuntimeError("Runtime context not initialized. Cannot access services.")
        
        # 懒加载缓存机制
        if not hasattr(self, '_call_service_proxy') or self._call_service_proxy is None:
            from sage.kernels.runtime.service.service_caller import ServiceCallProxy
            
            class ServiceProxy:
                def __init__(self, service_manager: 'ServiceManager', logger=None):
                    self._service_manager = service_manager
                    self._service_proxies = {}  # 缓存ServiceCallProxy对象
                    self.logger = logger if logger is not None else logging.getLogger(__name__)
                    
                def __getitem__(self, service_name: str):
                    if service_name not in self._service_proxies:
                        self._service_proxies[service_name] = ServiceCallProxy(
                            self._service_manager, service_name, logger=self.logger
                        )
                    return self._service_proxies[service_name]
            
            self._call_service_proxy = ServiceProxy(self.ctx.service_manager, logger=self.logger)
        
        return self._call_service_proxy
    
    @property 
    def call_service_async(self):
        """
        异步服务调用语法糖
        
        用法:
            future = self.call_service_async["cache_service"].get("key1")
            result = future.result()  # 阻塞等待结果
            
            # 或者非阻塞检查
            if future.done():
                result = future.result()
        """
        if self.ctx is None:
            raise RuntimeError("Runtime context not initialized. Cannot access services.")
        
        # 懒加载缓存机制
        if not hasattr(self, '_call_service_async_proxy') or self._call_service_async_proxy is None:
            class AsyncServiceProxy:
                def __init__(self, service_manager: 'ServiceManager', logger=None):
                    self._service_manager = service_manager
                    self._async_service_proxies = {}  # 缓存ServiceCallProxy对象
                    self.logger = logger if logger is not None else logging.getLogger(__name__)
                    
                def __getitem__(self, service_name: str):
                    if service_name not in self._async_service_proxies:
                        from sage.kernels.runtime.service.service_caller import ServiceCallProxy
                        self._async_service_proxies[service_name] = ServiceCallProxy(
                            self._service_manager, service_name, logger=self.logger
                        )
                    return self._async_service_proxies[service_name]
            
            self._call_service_async_proxy = AsyncServiceProxy(self.ctx.service_manager, logger=self.logger)
        
        return self._call_service_async_proxy

    # @abstractmethod
    # def close(self, *args, **kwargs):
    #     """
    #     Abstract method to be implemented by subclasses.

    #     Each rag must define its own execute logic that processes input data
    #     and returns the output.

    #     :param args: Positional input data.
    #     :param kwargs: Additional keyword arguments.
    #     :return: Output data.
    #     """
    #     pass


    @abstractmethod
    def execute(self, data:any):
        """
        Abstract method to be implemented by subclasses.

        Each rag must define its own execute logic that processes input data
        and returns the output.

        :param args: Positional input data.
        :param kwargs: Additional keyword arguments.
        :return: Output data.
        """
        pass

class MemoryFunction(BaseFunction):
    def __init__(self):
        self.ctx = None  # 需要在compiler里面实例化。
        self.memory= self.ctx.memory
        pass

class StatefulFunction(BaseFunction):
    """
    有状态算子基类：自动在 init 恢复状态，
    并可通过 save_state() 持久化。
    """
    # 子类可覆盖：只保存 include 中字段
    __state_include__ = []
    # 默认排除 logger、私有属性和 runtime_context
    __state_exclude__ = ['logger', '_logger', 'ctx']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 注入上下文
        # 恢复上次 checkpoint
        chkpt_dir = os.path.join(self.ctx.env_base_dir, ".sage_checkpoints")
        chkpt_path = os.path.join(chkpt_dir, f"{self.ctx.name}.chkpt")
        load_function_state(self, chkpt_path)

    def save_state(self):
        """
        将当前对象状态持久化到 disk，
        """
        base = os.path.join(self.ctx.env_base_dir, ".sage_checkpoints")
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, f"{self.ctx.name}.chkpt")
        save_function_state(self, path)