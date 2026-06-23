import json

from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.limit.tool import RateLimitTool
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
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
          
     async def execute(
          self,
          unique_handler_name: str,
          tool: RateLimitTool,
          event: TelegramObject,
          storage: BaseStorage,
          answer_callback: RateLimitAnswer
     ) -> bool:
          key = self.build_key(
               event=event,
               all_users=self.all_users,
               unique_handler_name=unique_handler_name
          )
          lock = self.get_lock(
               key=key,
               tool=tool
          )
          
          current_time = datetime.now(tz=timezone.utc)
          async with lock:
               times = await storage.get_value(key=key, prefix=tool.tool)
               if times is None:
                    await storage.set_value(
                         key=key,
                         value=json.dumps([current_time.isoformat()]),
                         prefix=tool.tool
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
                              prefix=tool.tool,
                              value=[timestamp.isoformat() for timestamp in active_user_time]
                         )
                    
                    await answer_callback(event, self.time, self.time - (current_time - active_user_time[0]))
                    return False

               active_user_time.append(current_time)
               await storage.set_value(
                    key=key,
                    prefix=tool.tool,
                    value=[timestamp.isoformat() for timestamp in active_user_time]
               )
               return True