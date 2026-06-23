from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.tools.limit.tool import RateLimitTool
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from .base import BaseRateLimit


class TokenBucketRateLimit(BaseRateLimit):
     
     def __init__(
          self,
          bucket_size: int,
          current_tokens: int,
          refill_time: timedelta,
          refill_tokens: int = 1,
          all_users: bool = False,
          time_before_one_token: bool = True
     ):
          self.bucket_size = bucket_size
          self.all_users = all_users
          self.current_tokens = current_tokens
          self.refill_rate = refill_tokens / refill_time.total_seconds()
          self.time_before_request = timedelta(
               seconds=(1 if time_before_one_token else bucket_size) / self.refill_rate
          )
     
     def count_new_tokens(
          self,
          current_tokens: int,
          current_time: datetime,
          last_time: datetime,
          refill_rate: int,
          bucket_size: int
     ) -> int | float:
          past_tense = (current_time - last_time).total_seconds()
          new_tokens = past_tense * refill_rate
          return min(bucket_size, current_tokens + new_tokens)
     
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
               bucket = await storage.get_value(prefix=tool.tool, key=key)
               if bucket is None:
                    await storage.set_value(
                         prefix=tool.tool,
                         key=key,
                         value=UserLimit(
                              requests=self.current_tokens - 1,
                              time=current_time
                         ).json()
                    )
                    return True
               
               bucket_limit = UserLimit.from_json(bucket)
               
               updated_tokens = self.count_new_tokens(
                    current_time=current_time,
                    last_time=bucket_limit.time,
                    current_tokens=bucket_limit.requests,
                    bucket_size=self.bucket_size,
                    refill_rate=self.refill_rate
               )
               
               if updated_tokens < 1:
                    await storage.set_value(
                         key=key,
                         prefix=tool.tool,
                         value=UserLimit(
                              requests=updated_tokens,
                              time=current_time
                         ).json()
                    )
                    tokens_needed = 1 - updated_tokens
                    seconds_to_wait = tokens_needed / self.refill_rate
                    await answer_callback(event, self.time_before_request, timedelta(seconds=seconds_to_wait))
                    return False
               
               await storage.set_value(
                    key=key,
                    prefix=tool.tool,
                    value=UserLimit(
                         requests=updated_tokens - 1,
                         time=current_time
                    ).json()
               )
               return True
               
               
               