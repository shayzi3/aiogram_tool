import asyncio

from redis.asyncio import Redis as AsyncRedis
from typing import Annotated
from contextlib import asynccontextmanager

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiotool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()


@asynccontextmanager
async def with_context():
     async with AsyncRedis() as session:
          try:
               yield session
          finally:
               await session.aclose()
       
       
               
async def without_context():
     async with AsyncRedis() as session:
          try:
               yield session
          finally:
               await session.aclose()



@dp.message(CommandStart())
async def start(
    message: Message,
    redis_session_with_context: Annotated[AsyncRedis, Depend(with_context)],
    redis_session_without_context: Annotated[AsyncRedis, Depend(without_context)]
):
    assert isinstance(redis_session_with_context, AsyncRedis)
    assert isinstance(redis_session_without_context, AsyncRedis)
    await message.answer("AsyncGenerator. Passed")
     
     
     
async def main():
    setup_depend_tool(dispatcher=dp)
    await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())