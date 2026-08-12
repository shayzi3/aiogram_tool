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
from aiogram_tool.tools.limit.rate_limit import FixedWindowRateLimit


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


@dp.message(
     # Limit: 3 requests per 10 seconds per user
     Command("ping"),
     RateLimitFilter(
          rate_limit=FixedWindowRateLimit(
               requests=3, 
               time=timedelta(seconds=10)
          )
     ),
)
async def ping_handler(message: Message):
    await message.answer("Pong!")


async def main():
     # Initialize and setup RateLimitTool
     # Uses MemoryLockStorage and default RateLimitAnswer by default
     rate_limit_tool = RateLimitTool()
     aiogram_tool_setup(dp, [rate_limit_tool])
     
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())