import asyncio

from redis.asyncio import Redis as AsyncRedis
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from aiogram_tool.limit import Limit, setup_limit_tool, RedisStorage




bot = Bot("TOKEN HERE")
dp = Dispatcher()



@dp.message(CommandStart(), Limit(seconds=5))
async def start(message: Message):
     await message.answer("Test RateLimit success")
     
     
@dp.message(Command("redis"), Limit(seconds=5, all_users=True))
async def all_users_redis(message: Message):
     await message.answer("All users Redis success.")
     
     
     
async def main():
     setup_limit_tool(
          dispatcher=dp,
          storage=RedisStorage(
               redis=AsyncRedis(decode_responses=True)
          )
     )
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())