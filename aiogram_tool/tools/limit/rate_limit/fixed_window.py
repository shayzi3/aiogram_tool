from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from aiogram_tool.types import _MISSING
from .base import BaseRateLimit



class FixedWindowRateLimit(BaseRateLimit):
     storage_prefix = "fixed_aiot_rate_limit"
     
     def __init__(
          self,
          requests: int,
          time: timedelta,
     ) -> None:
          """Fixed time window

          Args:
              requests (int): count of requests
              time (timedelta): window time
          """
          if requests <= 0:
               raise ValueError("requests must be greater than 0")
          
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
               
               raw_user_limit = await storage.get_value(key=key)
               if raw_user_limit is _MISSING:
                    await storage.set_value(
                         key=key,
                         value=UserLimit(
                              requests=self.requests - 1,
                              time=(current_time + self.time)
                         ).json()
                    )
                    return True

               user_limit = UserLimit.from_json(raw_user_limit)
               if current_time >= user_limit.time:
                    await storage.set_value(
                         key=key,
                         value=UserLimit(
                              requests=self.requests - 1,
                              time=(current_time + self.time)
                         ).json()
                    )
                    return True

               if user_limit.requests <= 0:
                    await answer_callback(event, self.time, user_limit.time - current_time)
                    return False

               user_limit.requests -= 1
               await storage.set_value(
                    key=key,
                    value=user_limit.json()
               )
               return True
          