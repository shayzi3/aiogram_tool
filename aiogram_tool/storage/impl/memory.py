from typing import Any
from cachetools import TTLCache

from aiogram_tool.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
     
     def __init__(self) -> None:
          self.storage: dict[str, Any] = {}
          
     def _check_prefix(self, prefix: str) -> None:
          if prefix not in self.storage.keys():
               self.storage[prefix] = {}
     
     async def set_value(self, key: str, value: Any, prefix: str) -> None:
          self._check_prefix(prefix=prefix)
          self.storage[prefix][key] = value
     
     async def get_value(self, key: str, prefix: str) -> Any:
          prefix_dict = self.storage.get(prefix, {})
          return prefix_dict.get(key, None)
     


class MemoryLimitStorage(MemoryStorage):
     
     def __init__(self, maxsize: int = 1000, ttl: int = 500) -> None:
          self.maxsize = maxsize
          self.ttl = ttl
          self.storage: dict[str, TTLCache] = {}
          
     def _check_prefix(self, prefix: str) -> None:
          if prefix not in self.storage:
               self.storage[prefix] = TTLCache(
                    maxsize=self.maxsize,
                    ttl=self.ttl
               )
     
     async def set_value(self, key: str, value: str, prefix: str) -> None:
          return await super().set_value(key=key, value=value, prefix=prefix)
          
     async def get_value(self, key: str, prefix: str) -> Any:
          return await super().get_value(key=key, prefix=prefix)
     
     
     
     