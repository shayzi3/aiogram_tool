import asyncio
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.limit import (
     RateLimitTool,
     RateLimitFilter
)
from aiogram_tool.tools.limit.rate_limit import (
     FixedWindowRateLimit,
     SlidingWindowRateLimit,
     TokenBucketRateLimit
)


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# 1. Fixed Window: 5 requests per 60 seconds
@dp.message(
     Command("fixed"),
     RateLimitFilter(
          rate_limit=FixedWindowRateLimit(
               requests=5, 
               time=timedelta(seconds=60)
          )
     ),
)
async def fixed_handler(message: Message):
     await message.answer("Fixed Window: Request allowed")


# 2. Sliding Window: 5 requests per 60 seconds
# More accurate than fixed window, prevents bursts at the edge of the window
@dp.message(
     Command("sliding"),
     RateLimitFilter(
          rate_limit=SlidingWindowRateLimit(
               requests=5, 
               time=timedelta(seconds=60)
          )
     ),
    
)
async def sliding_handler(message: Message):
     await message.answer("Sliding Window: Request allowed")


# 3. Token Bucket: 5 max tokens, starts with 5, refills 1 token every 5 seconds
@dp.message(
     Command("bucket"),
     RateLimitFilter(
          rate_limit=TokenBucketRateLimit(
               bucket_size=5,
               current_tokens=5,
               refill_time=timedelta(seconds=5),
               refill_tokens=1
          )
     ),
)
async def bucket_handler(message: Message):
     await message.answer("Token Bucket: Request allowed")


async def main():
     rate_limit_tool = RateLimitTool()
     aiogram_tool_setup(dp, [rate_limit_tool])
     
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())