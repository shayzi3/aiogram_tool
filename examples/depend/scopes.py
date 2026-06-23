import asyncio
import random

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.tools.depend import (
    Depends,
    setup_depend_tool,
    Scope,
    dependency_scope
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



class UserService:
     def __init__(self):
          self.number = random.randint(1, 10000)


@dependency_scope(scope=Scope.APP)
async def get_user_service():
     return UserService()



@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[UserService, Depends(get_user_service)],
):
     assert isinstance(service, UserService)
     await message.answer(f"Number {service.number}")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())