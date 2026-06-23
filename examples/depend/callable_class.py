import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.types.base import TelegramObject
from aiogram.filters import CommandStart

from aiogram_tool.tools.depend import (
    Depends,
    setup_depend_tool,
)



bot = Bot("7070441846:AAH36cRO3jzlvrHiypFYnJwHXmpB9lffbVc")
dp = Dispatcher()



class Service:
     def __init__(self, string: str):
          self.string = string
          
          
     async def __call__(self, event: TelegramObject) -> str:
          await event.answer("Hello from __call__ of class Service")
          return self.string
     
     
service = Service(string="my string")
          


@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[Service, Depends(service)],
):
     assert isinstance(service, str)
     await message.answer(service)
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())