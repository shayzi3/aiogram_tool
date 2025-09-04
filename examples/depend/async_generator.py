import asyncio

from redis.asyncio import Redis as AsyncRedis
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


async def session():
     async with AsyncRedis() as session:
          try:
               yield session
          finally:
               await session.aclose()



@dp.message(CommandStart())
async def start(
    message: Message,
    redis_session: Annotated[AsyncRedis, Depend(session)],
):
    assert isinstance(redis_session, AsyncRedis)
    await message.answer("AsyncGenerator. Passed")
     
     
     
async def main():
    setup_depend_tool(dispatcher=dp)
    await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())