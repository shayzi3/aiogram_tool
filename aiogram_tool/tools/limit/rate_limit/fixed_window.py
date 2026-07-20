from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from .base import BaseRateLimit



class FixedWindowRateLimit(BaseRateLimit):
     
     def __init__(
          self,
          requests: int,
          time: timedelta,
          all_users: bool = False
     ) -> None:
          self.requests = requests
          self.time = time
          self.all_users = all_users
          
     def build_key(
          self, 
          event: TelegramObject, 
          unique_handler_name: str
     ) -> str:
          user = str(event.from_user.id) if not self.all_users else "users"
          return f"{self.storage_prefix}@{user}@{unique_handler_name}"
          
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
               if raw_user_limit is None:
                    await storage.set_value(
                         key=key,
                         value=UserLimit(
                              requests=self.requests - 1,
                              time=(current_time + self.time)
                         ).json()
                    )
                    return True

               user_limit = UserLimit.from_json(raw_user_limit)
               if user_limit.compare_time_ge(current_time):
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
          