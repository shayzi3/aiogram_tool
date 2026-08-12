import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
     CallbackQuery,
     InlineKeyboardButton,
     InlineKeyboardMarkup,
     Message,
)
# Import LongCallbackData
from aiogram_tool.tools.callback_data import LongCallbackData


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Define callback data class
class MyLongData(LongCallbackData, prefix="mydata"):
     mode: str
     payload: str


async def get_keyboard() -> InlineKeyboardMarkup:
     # Pack short data (fits 64 bytes)
     short_data_cb = await MyLongData(mode="short", payload="Hello!").pack_long() # returns result of method 'pack'
     
     # Pack long data (exceeds 64 bytes)
     long_payload = "A" * 200
     long_data_cb = await MyLongData(mode="long", payload=long_payload).pack_long()

     return InlineKeyboardMarkup(
          inline_keyboard=[
               [InlineKeyboardButton(text="Short data", callback_data=short_data_cb)],
               [InlineKeyboardButton(text="Long data", callback_data=long_data_cb)],
          ]
     )


@dp.message(CommandStart())
async def start_handler(message: Message):
     await message.answer(
          text="Choose an action:",
          reply_markup=await get_keyboard(),
     )


# Use filter like standard aiogram
@dp.callback_query(MyLongData.filter(F.mode == "short"))
async def process_short_data(query: CallbackQuery, callback_data: MyLongData):
     await query.answer(text=f"Short data: {callback_data.payload}")


@dp.callback_query(MyLongData.filter(F.mode == "long"))
async def process_long_data(query: CallbackQuery, callback_data: MyLongData):
     # Receive original data even if it was long
     await query.answer(text=f"Long data received! Length: {len(callback_data.payload)}")


async def main():
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())