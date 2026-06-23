from typing import Any
from abc import ABC, abstractmethod


class BaseStorage(ABC):
     
     @abstractmethod
     async def set_value(self, key: str, value: str, prefix: str) -> None:
          raise NotImplementedError
          
     @abstractmethod
     async def get_value(self, key: str, prefix: str) -> Any:
          raise NotImplementedError
     
     def build_key(self, key: str, prefix: str, separator: str = "_") -> str:
          return separator.join([prefix, key])