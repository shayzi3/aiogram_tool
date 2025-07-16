import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiotool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("7984677679:AAFhTRbqUdaz_ocz-Rf5KZsTpMD5MEnP-84")
dp = Dispatcher()



class Service:
     def __init__(self):
          self.data = "data"
          
          
     async def __call__(self, event: Message) -> str:
          await event.answer("Hello from __call__ of class Service")
          return self.data
          


@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[Service, Depend(Service())],
):
     assert isinstance(service, str)
     await message.answer(service)
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())