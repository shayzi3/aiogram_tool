from typing import Any
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from aiogram_tool.types import NULL



class BaseStorage(ABC):
     
     @abstractmethod
     async def set_value(self, key: Any, value: Any) -> None:
          raise NotImplementedError
          
     @abstractmethod
     async def get_value(self, key: Any) -> Any | NULL:
          raise NotImplementedError
     
     
     
class BaseLockStorage(BaseStorage):
     
     @abstractmethod
     async def lock(self, key: Any) -> AbstractAsyncContextManager[None]:
          raise NotImplementedError