import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types.base import TelegramObject

from aiogram_tool.tools.depend import (
     DependHandler,
     DependExit,
     Depends
)

bot = Bot("7070441846:AAH36cRO3jzlvrHiypFYnJwHXmpB9lffbVc")
dp = Dispatcher()


users = {"shayZi1234": 10}


async def user_register(event: TelegramObject) -> None:
     username = event.from_user.username
     
     if username not in users.keys():
          return DependExit(event=event, text="Not found balance.")
     await event.answer(text=f"Your balance {users[username]}")
     

@dp.message(CommandStart(), DependHandler(Depends(user_register)))
async def start(message: Message):
     await message.answer(f"Hello!")  
     
     
async def main():
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())