from typing import Iterable
from abc import ABC, abstractmethod

from aiogram import Dispatcher

from aiogram_tool.storage.base import BaseStorage


class BaseTool(ABC):
     __tool__: str
     
     @abstractmethod
     def setup(
          self, 
          dispatcher: Dispatcher, 
          storage: BaseStorage | None = None
     ) -> None:
          ...
          
     @property
     def tool(self) -> str:
          return self.__tool__


def aiogram_tool_setup(
     dispatcher: Dispatcher,
     tools: Iterable[BaseTool],
     storage: BaseStorage | None = None,
) -> None:
     if not isinstance(dispatcher, Dispatcher):
          raise TypeError("Invalid type for dispatcher")
     
     if not isinstance(storage, BaseStorage):
          raise TypeError(f"Invalid type for storage {storage}")
     
     for tool in tools:
          if not isinstance(tool, BaseTool):
               raise TypeError(f"Invalid type for tool {tool}")
          else:          
               tool.setup(dispatcher=dispatcher, storage=storage)