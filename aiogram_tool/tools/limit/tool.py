from aiogram import Dispatcher

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.storage.impl.memory import MemoryLockStorage
from aiogram_tool.tools.setup import BaseTool
from aiogram_tool.tools.limit.answer import RateLimitAnswer

     



class RateLimitTool(BaseTool):
     """Tool for verifying the request limiter's functionality"""
     
     def __init__(
          self,
          storage: BaseLockStorage | None = None,
          answer_callback: RateLimitAnswer | None = None
     ) -> None:
          self.storage = storage or MemoryLockStorage()
          self.answer_callback = answer_callback or RateLimitAnswer()
          
     def setup(self, dispatcher: Dispatcher) -> None:
          dispatcher.workflow_data["rate_limit"] = self