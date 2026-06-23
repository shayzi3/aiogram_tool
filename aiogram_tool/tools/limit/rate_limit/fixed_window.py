from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from aiogram_tool.tools.limit.tool import RateLimitTool
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
               limit = await storage.get_value(key=key, prefix=tool.tool)
               if limit is None:
                    await storage.set_value(
                         key=key,
                         prefix=tool.tool,
                         value=UserLimit(
                              requests=self.requests - 1,
                              time=(current_time + self.time)
                         ).json()
                    )
                    return True

               user_limit = UserLimit.from_json(limit)
               if user_limit.compare_time_ge(current_time):
                    await storage.set_value(
                         key=key,
                         prefix=tool.tool,
                         value=UserLimit(
                              requests=self.requests - 1,
                              time=(current_time + self.time)
                         ).json()
                    )
                    return True

               if user_limit.requests == 0:
                    await answer_callback(event, self.time, user_limit.time - current_time)
                    return False

               await storage.set_value(
                    key=key,
                    prefix=tool.tool,
                    value=UserLimit(
                         requests=user_limit.requests - 1,
                         time=user_limit.time
                    ).json()
               )
               return True
          