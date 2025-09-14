from typing import Any



class DataStorage:
     def __init__(self):
          self._data: dict[str, Any] = {}
     
     def set_value(self, key: str, value: Any) -> None:
          self._data[key] = value
          
     def get_value(self, key: str) -> Any:
          return self._data.get(key)
     
     
data_storage = DataStorage()
     