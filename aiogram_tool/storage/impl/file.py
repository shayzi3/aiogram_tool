import aiofiles

from typing import Any

from aiogram_tool.storage.base import BaseStorage



class FileStorage(BaseStorage):
     
     def __init__(self, file: str) -> None:
          try:
               with open(file, "r"): ...
          except FileNotFoundError as ex:
               raise FileNotFoundError(f"File {file} not found") from ex
          
          self.file = file
          
     async def set_value(self, key: str, value: str, prefix: str) -> None:
          if "&" in value:
               raise ValueError(f"Symbol & can't use in value {value}")
          
          key_with_prefix = self.build_key(key, prefix)
          async with aiofiles.open(self.file, "a") as aiofile:
               await aiofile.write(f"\n{key_with_prefix}&{value}")
            
     async def get_value(self, key: str, prefix: str) -> Any:
          async with aiofiles.open(self.file, "r") as aiofile:
               data = await aiofile.read()
          
          key_with_prefix = self.build_key(key, prefix)
          split_data = data.split("\n")
          if split_data:
               for field in split_data:
                    if field:
                         try:
                              field_key, value = field.rsplit("&")
                         except ValueError as ex:
                              raise ValueError(f"Invalid field in file {field}") from ex
                         else:
                              if key_with_prefix == field_key:
                                   return value
               
          
               
     
     
     