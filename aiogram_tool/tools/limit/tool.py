from aiogram import Dispatcher

from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.storage.impl.memory import MemoryLockStorage
from aiogram_tool.tools.setup import BaseTool
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer

     



class RateLimitTool(BaseTool):
     
     def __init__(
          self,
          storage: BaseLockStorage = MemoryLockStorage(),
          answer_callback: RateLimitAnswer = RateLimitAnswer(),
     ) -> None:
          if not isinstance(storage, BaseLockStorage):
               raise TypeError(f"Invalid type for storage {storage}")
          
          if not isinstance(answer_callback, RateLimitAnswer):
               raise TypeError(f"Invalid type for answer_callback {answer_callback}")
          
          self.storage = storage
          self.answer_callback = answer_callback
          
     def setup(self, dispatcher: Dispatcher) -> None:
          dispatcher.workflow_data["rate_limit"] = self