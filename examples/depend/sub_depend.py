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



async def redis_session():
     async with AsyncRedis(decode_responses=True) as session:
          try:
               yield session
          finally:
               await session.aclose()


async def get_name_from_redis(session: Annotated[AsyncRedis, Depend(redis_session)]):
     return await session.get("user")


@dp.message(CommandStart())
async def start(
     message: Message,
     user_name: Annotated[str, Depend(get_name_from_redis)]
):
     assert isinstance(user_name, str)
     await message.answer(f"Hello {user_name}")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())