import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



class Service:
     def __init__(self, string: str):
          self.string = string
          
          
     async def __call__(self, event: Message) -> str:
          await event.answer("Hello from __call__ of class Service")
          return self.string
     
     
service = Service(string="my string")
          


@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[Service, Depend(service)],
):
     assert isinstance(service, str)
     await message.answer(service)
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())