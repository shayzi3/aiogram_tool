import asyncio

from redis import Redis
from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.tools.depend import (
    Depends,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



def session():
     with Redis() as session:
          try:
               yield session
          finally:
               session.close()



@dp.message(CommandStart())
async def start(
     message: Message,
     redis_session: Annotated[Redis, Depends(session)],
):
     assert isinstance(redis_session, Redis)
     await message.answer("SyncGenerator. Passed")
     
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())