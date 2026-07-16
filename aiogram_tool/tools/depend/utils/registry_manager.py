from typing_extensions import Self
from typing import Callable, Any, MutableMapping
from contextlib import nullcontext
from asyncio import Lock

from aiogram_tool.types import _MISSING
from aiogram_tool.storage.impl.memory import MemoryLockStorage, MemoryStorage
from aiogram_tool.tools.depend.types.enums import Scope


          
     
class DependRegistryTransaction:
     
     def __init__(self, app_storage: MemoryLockStorage) -> None:
          self.app_storage = app_storage
          self.storage = MemoryStorage()
          
     async def __aenter__(self) -> Self:
          return self
     
     async def __aexit__(self, *args) -> None:
          memory_storage: MutableMapping = getattr(self.storage, "storage")
          memory_storage.clear()
          
     def _get_storage(self, scope: Scope) -> MemoryLockStorage | MemoryStorage | _MISSING:
          if scope == Scope.SINGLETON:
               return self.app_storage
          elif scope == Scope.REQUEST:
               return self.storage
          elif scope == Scope.TRANSIENT:
               return _MISSING
          
     def _get_lock_storage(self, scope: Scope) -> MemoryLockStorage | _MISSING:
          if scope == Scope.SINGLETON:
               return self.app_storage
          return _MISSING
          
     async def get_value(
          self,
          func: Callable,
          scope: Scope
     ) -> Any | _MISSING:
          storage = self._get_storage(scope)
          if storage is not _MISSING:
               return await storage.get_value(key=func)
          return _MISSING
     
     async def set_value(
          self,
          func: Callable,
          scope: Scope,
          depend_result: Any
     ) -> None:
          storage = self._get_storage(scope)
          if storage is not _MISSING:
               await storage.set_value(key=func, value=depend_result)
          
     async def lock(
          self, 
          key: Callable,
          scope: Scope
     ) -> Lock | nullcontext:
          storage = self._get_lock_storage(scope)
          if storage is not _MISSING:
               return await storage.lock(key=key)
          return nullcontext()
          
          
class DependRegistryTransactionManager:
     
     def __init__(self) -> None:
          self.storage = MemoryLockStorage()
     
     def transaction(self) -> DependRegistryTransaction:
          return DependRegistryTransaction(self.storage)
     
     
          
     