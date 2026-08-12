import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
     CallbackQuery,
     InlineKeyboardButton,
     InlineKeyboardMarkup,
     Message,
)
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.tools.callback_data import LongCallbackData
# Import Redis storage
from aiogram_tool.storage import AsyncRedisLockStorage


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()

# Init Redis storage (expire in 3600 seconds)
redis_client = AsyncRedis(host="localhost", port=6379, decode_responses=True)
redis_storage = AsyncRedisLockStorage(redis=redis_client, expire=3600)


# Override _storage to use Redis
class PersistentData(LongCallbackData, prefix="redis"):
     _storage = redis_storage
     
     user_id: int
     action: str
     big_context: str


async def get_keyboard(user_id: int) -> InlineKeyboardMarkup:
    # Data saves in Redis. Survives bot restarts until TTL expires
     callback_data = await PersistentData(
          user_id=user_id,
          action="view_profile",
          big_context="x" * 150
     ).pack_long()

     return InlineKeyboardMarkup(
          inline_keyboard=[
               [InlineKeyboardButton(text="Open profile", callback_data=callback_data)]
          ]
     )


@dp.message(CommandStart())
async def start_handler(message: Message):
     await message.answer(
          text="Keyboard with Redis storage:",
          reply_markup=await get_keyboard(message.from_user.id),
     )


@dp.callback_query(PersistentData.filter(F.action == "view_profile"))
async def process_view_profile(query: CallbackQuery, callback_data: PersistentData):
     await query.answer(
          text=f"Profile of {callback_data.user_id}. Data is valid."
     )


async def main():
     try:
          await dp.start_polling(bot)
     finally:
         await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())