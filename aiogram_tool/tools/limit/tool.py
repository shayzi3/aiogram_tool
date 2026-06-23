from cachetools import TTLCache
from aiogram import Dispatcher

from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.setup import BaseTool
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer

     



class RateLimitTool(BaseTool):
     __tool__ = "rate_limit"
     
     def __init__(
          self,
          storage: BaseStorage | None = None,
          answer_callback: RateLimitAnswer = RateLimitAnswer(),
          user_locks_maxsize: int = 10000,
          user_locks_ttl: int = 500
     ) -> None:
          if not isinstance(storage, BaseStorage):
               raise TypeError(f"Invalid type for storage {storage}")
          
          if not isinstance(answer_callback, RateLimitAnswer):
               raise TypeError(f"Invalid type for answer_callback {answer_callback}")
          
          self.storage = storage
          self.answer_callback = answer_callback
          self.locks = TTLCache(
               maxsize=user_locks_maxsize,
               ttl=user_locks_ttl
          )
          
     def setup(
          self, 
          dispatcher: Dispatcher,
          storage: BaseStorage | None = None,
     ) -> None:
          if self.storage is None:
               self.storage = storage
          dispatcher.workflow_data[self.tool] = self