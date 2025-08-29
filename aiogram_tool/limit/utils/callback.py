import inspect

from typing import Callable, Any

from datetime import timedelta, datetime
from aiogram.types.base import TelegramObject



class AnswerCallback:
     def __init__(self, obj: Callable[[TelegramObject, timedelta, datetime], Any]):
          self._isasync = False
          self._obj = obj
          
          if not callable(self._obj):
               raise ValueError("obj in AnswerCallback must be callable")
          
          self.__explore_obj()
          
     
     def __explore_obj(self) -> None:
          if not inspect.isfunction(self._obj):
               self._obj = getattr(self._obj, "__call__", None)
               if self._obj is None:
                    raise ValueError(f"don't find method __call__ at obj")
               
          if inspect.iscoroutinefunction(self._obj):
               self._isasync = True
          else:
               self._isasync = False
          
          
     async def call(
          self, 
          event: TelegramObject, 
          rate_time: timedelta, 
          time_last: datetime
     ) -> Any:
          calling = self._obj(event, rate_time, time_last)
          return await calling if self._isasync else calling