import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.depend import (
    Depend,
    setup_depend_tool,
    Scope,
    dependency_scope
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



class UserService:
     pass


@dependency_scope(scope=Scope.APP)
async def get_user_service():
     return UserService()



@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[UserService, Depend(get_user_service)],
):
     assert isinstance(service, UserService)
     await message.answer("Default. Passed")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())