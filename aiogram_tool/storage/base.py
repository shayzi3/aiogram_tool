from typing import Any
from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class BaseStorage(ABC):
     
     @abstractmethod
     async def set_value(self, key: str, value: str) -> None:
          raise NotImplementedError
          
     @abstractmethod
     async def get_value(self, key: str) -> Any:
          raise NotImplementedError
     
     
     
class BaseLockStorage(BaseStorage):
     
     @abstractmethod
     async def lock(self, key: str) -> AbstractAsyncContextManager[None]:
          raise NotImplementedError