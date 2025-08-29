from aiogram import Dispatcher

from .utils.callback import AnswerCallback
from .storage.abstract_storage import AbstractStorage
from .storage import MemoryStorage



def setup_limit_tool(
     dispatcher: Dispatcher,
     storage: AbstractStorage = MemoryStorage(),
     answer_callback: AnswerCallback | None = None
) -> None:
     if not isinstance(dispatcher, Dispatcher):
          raise TypeError("Invalid type for dispatcher")
     
     if not issubclass(type(storage), AbstractStorage):
          raise TypeError("Invalid type for storage")
     
     if answer_callback is not None:
          if not isinstance(answer_callback, AnswerCallback):
               raise TypeError("Invalid type for answer_callback")
     
     dispatcher["storage"] = storage
     dispatcher["answer_callback"] = answer_callback