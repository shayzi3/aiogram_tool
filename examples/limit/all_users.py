import asyncio

from datetime import datetime, timedelta
from typing import Any

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.limit import Limit



bot = Bot("TOKEN HERE")
dp = Dispatcher()



@dp.message(CommandStart(), Limit(seconds=5, all_users=True))
async def start(message: Message):
     # All users restricts the use of the command for all users
     await message.answer("Test RateLimit success")
     
     
async def main():
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())