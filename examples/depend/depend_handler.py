import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types.base import TelegramObject

from aiogram_tool.depend import (
     DependHandler,
     DependExit,
     Depend
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()


users = {
     "name": "balance"
}


async def user_register(event: TelegramObject) -> None:
     username = event.from_user.username
     
     if username not in users:
          return DependExit(event=event, text="Not found balance.")
     return f"Your balance {username}"
     

@dp.message(CommandStart(), DependHandler(Depend(user_register)))
async def start(message: Message):
     await message.answer(f"Hello!")  
     
     
async def main():
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())