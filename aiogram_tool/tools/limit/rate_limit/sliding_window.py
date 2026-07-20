import json

from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from .base import BaseRateLimit



class SlidingWindowRateLimit(BaseRateLimit):
     
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
               
               times = await storage.get_value(key=key)
               if times is None:
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

                    await answer_callback(event, self.time, self.time - (current_time - active_user_time[0]))
                    return False

               active_user_time.append(current_time)
               await storage.set_value(
                    key=key,
                    value=json.dumps([timestamp.isoformat() for timestamp in active_user_time])
               )
               return True