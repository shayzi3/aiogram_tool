from dataclasses import dataclass

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.utils.answer import CallbackDataAnswer
from .utils.answer_callback import callback



@dataclass
class CallbackDataConfig:
     storage: BaseStorage
     answer: CallbackDataAnswer = CallbackDataAnswer(obj=callback)
     
     def __post_init__(self) -> None:
          if not isinstance(self.storage, BaseStorage):
               raise TypeError(f"Invalid type for storage {self.storage}")
          
          if not isinstance(self.answer, CallbackDataAnswer):
               raise TypeError(f"Invalid type for answer {self.answer}")
          
     @property
     def tool(self) -> str:
          return "callback_data"

