from aiogram import Dispatcher
from aiogram.filters import Filter
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject

from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.limit.rate_limit.base import BaseRateLimit
from aiogram_tool.tools.limit.tool import RateLimitTool




class RateLimitFilter(Filter):
     
     def __init__(
          self,
          rate_limit: BaseRateLimit,
          storage: BaseStorage | None = None,
          answer_callback: RateLimitAnswer | None = None
     ) -> None:
          if not isinstance(storage, BaseStorage):
               raise TypeError(f"Invalid type for storage {storage}")
          
          if not isinstance(answer_callback, RateLimitAnswer):
               raise TypeError(f"Invalid type for answer_callback {answer_callback}")
          
          if not isinstance(rate_limit, BaseRateLimit):
               raise TypeError(f"Invalid type for rate_limit {rate_limit}")

          self.storage = storage
          self.answer_callback = answer_callback
          self.rate_limit = rate_limit
          
     def get_rate_limit_tool(self, dispatcher: Dispatcher) -> RateLimitTool:
          rate_limit_tool: RateLimitTool = dispatcher.workflow_data.get("rate_limit", None)
          if rate_limit_tool is None:
               raise ValueError("Not found RateLimitTool. Call setup function")
          return rate_limit_tool
     
     def unique_handler_name(self, handler: HandlerObject) -> str:
          callback = handler.callback
          return getattr(callback, "__name__") + str(hash(callback))
          
     async def __call__(
          self, 
          event: TelegramObject,
          handler: HandlerObject,
          dispatcher: Dispatcher
     ) -> bool:
          rate_limit_tool = self.get_rate_limit_tool(dispatcher)
          
          if self.storage is None:
               if rate_limit_tool.storage is None:
                    raise TypeError()
               self.storage = rate_limit_tool.storage
               
          if self.answer_callback is None:
               self.answer_callback = rate_limit_tool.answer_callback
               
          unique_name = self.unique_handler_name(handler)
          return await self.rate_limit.execute(
               event=event,
               storage=self.storage,
               answer_callback=self.answer_callback,
               unique_handler_name=unique_name,
               tool=rate_limit_tool
          )
          