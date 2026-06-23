import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.tools.depend import (
    Depends,
    setup_depend_tool,
)


bot = Bot("7070441846:AAH36cRO3jzlvrHiypFYnJwHXmpB9lffbVc")
dp = Dispatcher()



class UserService:
     pass


async def get_user_service():
     return UserService()


@dp.message(CommandStart())
async def start(
     message: Message,
     service: Annotated[UserService, Depends(get_user_service)],
):
     assert isinstance(service, UserService)
     await message.answer("Default. Passed")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())