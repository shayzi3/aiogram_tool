import json

from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from aiogram_tool.types import _MISSING
from .base import BaseRateLimit



class SlidingWindowRateLimit(BaseRateLimit):
     storage_prefix = "sliding_aiot_rate_limit"
     
     def __init__(
          self,
          requests: int,
          time: timedelta,
     ) -> None:
          self.requests = requests
          self.time = time
          
     async def execute(
          self,
          event: TelegramObject,
          storage: BaseLockStorage,
          answer_callback: RateLimitAnswer,
          key: str
     ) -> bool:
          lock = await storage.lock(key)
          async with lock:
               current_time = datetime.now(tz=timezone.utc)
               
               times = await storage.get_value(key=key)
               if times is _MISSING:
                    await storage.set_value(
                         key=key,
                         value=json.dumps([current_time.isoformat()]),
                    )
                    return True

               user_time = [
                    datetime.fromisoformat(date) 
                    for date in json.loads(times)
               ]
               active_user_time = [
                    timestamp
                    for timestamp in user_time
                    if (current_time - timestamp) < self.time
               ]
               if len(active_user_time) >= self.requests:
                    if len(active_user_time) != len(user_time):
                         await storage.set_value(
                              key=key,
                              value=json.dumps([timestamp.isoformat() for timestamp in active_user_time])
                         )

                    await answer_callback(event, self.time, self.time - (current_time - min(active_user_time)))
                    return False

               active_user_time.append(current_time)
               await storage.set_value(
                    key=key,
                    value=json.dumps([timestamp.isoformat() for timestamp in active_user_time])
               )
               return True