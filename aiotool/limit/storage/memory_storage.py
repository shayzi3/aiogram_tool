from datetime import datetime

from .abstract_storage import AbstractStorage



class DataStorage:
     data: dict[str, datetime] = {}
     
     


class MemoryStorage(AbstractStorage):
     def __init__(self):
          self.storage = DataStorage
     
     
     async def get(self, name: str) -> datetime | None:
          return self.storage.data.get(name)
     
     
     async def update(self, name: str, value: datetime) -> None:
          self.storage.data.update({name: value})