from abc import ABC, abstractmethod
from datetime import datetime



class AbstractStorage(ABC):
     
     
     @abstractmethod
     async def get(self, name: str) -> datetime | None:
          raise NotImplementedError
     
     
     @abstractmethod
     async def update(self, name: str, value: datetime) -> None:
          raise NotImplementedError