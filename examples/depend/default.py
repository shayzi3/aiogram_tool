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



class UserService:

     @classmethod
     async def get_service(cls) -> "UserService":
          return cls()
     
     
     @classmethod
     def sync_get_service(cls) -> "UserService":
          return cls()



@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[UserService, Depend(UserService.get_service)],
     sync_service: Annotated[UserService, Depend(UserService.sync_get_service)]
):
     assert isinstance(service, UserService)
     assert isinstance(sync_service, UserService)
     await message.answer("Default. Passed")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())