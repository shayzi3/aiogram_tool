import asyncio
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, TelegramObject
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.limit import (
     RateLimitTool,
     RateLimitFilter,
     RateLimitAnswer
)
from aiogram_tool.tools.limit.rate_limit import SlidingWindowRateLimit
from aiogram_tool.storage import AsyncRedisLockStorage


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Custom answer callback when limit is exceeded
class CustomLimitAnswer(RateLimitAnswer):
     async def __call__(
          self, 
          event: TelegramObject, 
          window_time: timedelta, 
          retry_after: timedelta
     ) -> None:
          await event.answer(
               text=f"🚫 Slow down! Try again in {retry_after.total_seconds():.1f} seconds."
          )


@dp.message(
     # all_users=True applies limit globally, not per user
     # key="global_start" overrides the default handler-based key
     Command("start"),
     RateLimitFilter(
          rate_limit=SlidingWindowRateLimit(
               requests=10, 
               time=timedelta(minutes=1)
          ),
          all_users=True,
          key="global_start"
     ),
)
async def start_handler(message: Message):
    await message.answer("Global limit for /start command. (10 requests/min globally)")


@dp.message(
     # Per-handler filter with a custom local answer callback
     Command("secret"),
     RateLimitFilter(
          rate_limit=SlidingWindowRateLimit(
               requests=2, 
               time=timedelta(seconds=30)
          ),
          answer_callback=RateLimitAnswer() # Overrides tool's answer_callback
     ),
)
async def secret_handler(message: Message):
    await message.answer("Secret command. Limit: 2 requests per 30 seconds.")


async def main():
     redis_storage = AsyncRedisLockStorage(redis=AsyncRedis())
     
     rate_limit_tool = RateLimitTool(
         storage=redis_storage,
         answer_callback=CustomLimitAnswer()
     )
     aiogram_tool_setup(dp, [rate_limit_tool])
     
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())