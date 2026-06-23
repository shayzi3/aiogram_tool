import asyncio

from redis.asyncio import Redis as AsyncRedis
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


async def session():
     async with AsyncRedis() as session:
          try:
               print("session open")
               yield session
          finally:
               await session.aclose()
               print("session close")



@dp.message(CommandStart())
async def start(
    message: Message,
    redis_session: Annotated[AsyncRedis, Depends(session)],
):
    assert isinstance(redis_session, AsyncRedis)
    await message.answer("AsyncGenerator. Passed")
    print("handler")
     
     
     
async def main():
    setup_depend_tool(dispatcher=dp)
    await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())