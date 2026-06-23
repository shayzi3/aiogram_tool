from typing import Any
from abc import ABC, abstractmethod




class BaseAnswer(ABC):
     
     @abstractmethod
     async def __call__(
          self,
          *args: Any,
          **kwargs: Any
     ) -> Any:
          raise NotImplementedError