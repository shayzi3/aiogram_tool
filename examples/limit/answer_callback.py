import asyncio

from datetime import datetime, timedelta
from typing import Any

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.types.base import TelegramObject
from aiogram.filters import CommandStart

from aiogram_tool.limit import Limit, setup_limit_tool




bot = Bot("TOKEN HERE")
dp = Dispatcher()




@dp.message(CommandStart(), Limit(seconds=5))
async def start(message: Message):
     await message.answer("Test RateLimit success")
     
     
     
async def rate_limit_answer(
     message: TelegramObject, 
     time: timedelta, # Time at handler
     lost_time: datetime # Time to next execution of the request
) -> Any:
     return await message.answer(
          f"До следующего использования команды: {lost_time.total_seconds()}"
     )
     
     
     
async def main():
     setup_limit_tool(
          dispatcher=dp,
          answer_callback=rate_limit_answer
     )
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())