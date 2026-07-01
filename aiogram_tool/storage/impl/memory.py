from typing import Any, Hashable
from asyncio import Lock
from collections.abc import MutableMapping

from aiogram_tool.storage.base import BaseStorage, BaseLockStorage


class MemoryStorage(BaseStorage):
     
     def __init__(self, storage: MutableMapping | None = None) -> None:
          self.storage = storage if storage else {}
          
     async def set_value(self, key: Hashable, value: Any) -> None:
          self.storage[key] = value
          
     async def get_value(self, key: Hashable) -> Any:
          return self.storage.get(key, None)
     

class MemoryLockStorage(MemoryStorage, BaseLockStorage):
     
     def __init__(
          self, 
          storage: MutableMapping | None = None,
          locks_storage: MutableMapping | None = None
     ) -> None:
          self.global_lock = Lock()
          self.locks = locks_storage if locks_storage else {}
          super().__init__(storage=storage)
     
     async def lock(self, key: str) -> Lock:
          async with self.global_lock:
               if key not in self.locks.keys():
                    self.locks[key] = Lock()
               return self.locks[key]
          