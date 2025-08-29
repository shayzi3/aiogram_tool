import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.depend import (
     Depend, 
     setup_depend_tool,
     DependExit
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



async def some_dependency(event: Message) -> str:
     if "s" not in event.from_user.username:
          return f"Hello {event.from_user.username}"
     return DependExit(event=event, text=f"Bye {event.from_user.username}")
     
     
@dp.message(CommandStart())
async def start(
     message: Message,
     some_string: str = Depend(some_dependency)
):
     await message.answer(some_string)  
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())