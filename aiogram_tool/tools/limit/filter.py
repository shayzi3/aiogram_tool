from aiogram import Dispatcher
from aiogram.filters import Filter
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject

from aiogram_tool.tools.limit.answer import RateLimitAnswer
from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.rate_limit.base import BaseRateLimit
from aiogram_tool.tools.limit.tool import RateLimitTool




class RateLimitFilter(Filter):
     """Class for request limits on the handler"""
     
     def __init__(
          self,
          rate_limit: BaseRateLimit,
          storage: BaseLockStorage | None = None,
          answer_callback: RateLimitAnswer | None = None,
          key: str | None = None,
          all_users: bool = False
     ) -> None:
          """
          Args:
               rate_limit - type of request limiter
               storage - custom storage for scpecific handler
               answer_callback - custom callback for specific handler
               key - Key for identifying the handler. By default, the handler name and module are used.
               all_users - Limit for all users simultaneously

          """
          self.storage = storage
          self.answer_callback = answer_callback
          self.rate_limit = rate_limit
          self.all_users = all_users
          self.key = key
          
     def get_rate_limit_tool(self, **kwargs) -> RateLimitTool:
          dispatcher: Dispatcher = kwargs.get("dispatcher")
          if dispatcher is None:
               raise ValueError("Dispatcher not found")
          
          rate_limit_tool: RateLimitTool = dispatcher.workflow_data.get("rate_limit")
          if rate_limit_tool is None:
               raise ValueError("Not found RateLimitTool. Call setup function")
          return rate_limit_tool
     
     def unique_handler_name(self, **kwargs) -> str:
          handler: HandlerObject = kwargs.get("handler")
          if handler is None:
               raise ValueError("Handler not found")
          
          callback = handler.callback
          
          module = getattr(callback, "__module__")
          qualname = getattr(callback, "__qualname__")
          return f"{module}.{qualname}"
          
     async def __call__(self, *args, **kwargs) -> bool:
          event: TelegramObject = args[0]
          rate_limit_tool = self.get_rate_limit_tool(**kwargs)
          
          storage = self.storage
          if storage is None:
               storage = rate_limit_tool.storage
               
          answer_callback = self.answer_callback
          if answer_callback is None:
               answer_callback = rate_limit_tool.answer_callback
               
          unique_key = self.rate_limit.build_key(
               event=event,
               unique_handler_name=self.unique_handler_name(**kwargs),
               all_users=self.all_users,
               key=self.key
          )
          return await self.rate_limit.execute(
               event=event,
               storage=storage,
               answer_callback=answer_callback,
               key=unique_key
          )
          