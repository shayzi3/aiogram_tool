from typing_extensions import Callable, Self, Any

from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.tools.depend.types.enums import Scope



     
class DependRegistryTransaction(MemoryStorage):
     
     def __init__(self, app_storage: MemoryStorage) -> None:
          self.app_storage = app_storage
          super().__init__()
          
     async def __aenter__(self) -> Self:
          return self
     
     async def __aexit__(self, *args) -> None:
          self.storage.clear()
          
     async def get_cached_depend(
          self,
          func: Callable,
          scope: Scope
     ) -> Any:
          storage = None
          if scope == Scope.APP:
               storage = self.app_storage
          elif scope == Scope.REQUEST:
               storage = self
          else:
               return None
          return await storage.get_value(key=hash(func))
     
     async def set_cached_depend(
          self,
          func: Callable,
          scope: Scope,
          depend_result: Any
     ) -> None:
          storage = None
          if scope == Scope.APP:
               storage = self.app_storage
          elif scope == Scope.REQUEST:
               storage = self
          else:
               return None
          await storage.set_value(key=hash(func), value=depend_result)
          
          
          
class DependRegistryTransactionManager(MemoryStorage):
     
     def transaction(self) -> DependRegistryTransaction:
          return DependRegistryTransaction(self)
     
     
          
     