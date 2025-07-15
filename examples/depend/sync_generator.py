import asyncio

from redis import Redis
from typing import Annotated
from contextlib import contextmanager

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiotool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()


@contextmanager
def with_context():
     with Redis() as session:
          try:
               yield session
          finally:
               session.close()
       
       
               
def without_context():
     with Redis() as session:
          try:
               yield session
          finally:
               session.close()        



@dp.message(CommandStart())
async def start(
     message: Message,
     redis_session_with_context: Annotated[Redis, Depend(with_context)],
     redis_session_without_context: Annotated[Redis, Depend(without_context)]
):
     assert isinstance(redis_session_with_context, Redis)
     assert isinstance(redis_session_without_context, Redis)
     await message.answer("SyncGenerator. Passed")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())