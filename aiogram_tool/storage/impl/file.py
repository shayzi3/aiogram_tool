import aiofiles
import os

from asyncio import Lock
from typing import Any
from collections.abc import MutableMapping

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.storage.impl.memory import MemoryStorage


class FileStorage(MemoryStorage):
     
     def __init__(
          self, 
          file: str,
          memory: bool = True,
          storage: MutableMapping | None = None
     ) -> None:
          if not os.path.exists(file):
               raise FileNotFoundError(f"File {file} not found")
          
          self.memory = memory
          self.file = file
          
          if memory:
               super().__init__(storage=storage)
          
     async def set_value(self, key: str, value: str) -> None:
          if "&" in key:
               raise ValueError(f"Symbol & can't use in key {value}")
          
          async with aiofiles.open(self.file, "a") as aiofile:
               await aiofile.write(f"\n{key}&{value}")
          
          if self.memory:
               super().set_value(key=key, value=value)
            
     async def get_value(self, key: str) -> Any:
          if self.memory:
               value = super().get_value(key=key)
               if value:
                    return value
               
          async with aiofiles.open(self.file, "r") as aiofile:
               data = await aiofile.readlines()
               data.reverse()
               
          for line in data:
               line_key, line_value = line.split(sep="&", maxsplit=1)
               if line_key == key:
                    if self.memory:
                         await super().set_value(key, line_value)
                    return line_value
          
                              
                              
class FileLockStorage(FileStorage, BaseLockStorage):
     
     def __init__(
          self,
          file: str,
          memory: bool = True,
          storage: MutableMapping | None = None,
          locks_storage: MutableMapping | None = None
     ) -> None:
          self.global_lock = Lock()
          self.locks = locks_storage if locks_storage else {}
          super().__init__(
               file=file,
               memory=memory,
               storage=storage
          )
     
     async def lock(self, key: str) -> Lock:
          async with self.global_lock:
               if key not in self.locks.keys():
                    self.locks[key] = Lock()
               return self.locks[key]
               
          
               
     
     
     