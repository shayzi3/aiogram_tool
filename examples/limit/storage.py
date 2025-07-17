import asyncio

from redis.asyncio import Redis as AsyncRedis
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_tool.limit import Limit, setup_limit_tool
from aiogram_tool.limit.storage import RedisStorage




bot = Bot("TOKEN HERE")
dp = Dispatcher()



@dp.message(CommandStart(), Limit(seconds=5))
async def start(message: Message):
     await message.answer("Test RateLimit success")
     
     
     
async def main():
     setup_limit_tool(
          dispatcher=dp,
          storage=RedisStorage(
               redis=AsyncRedis() # MemoryStorage is default parametr
          )
     )
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())