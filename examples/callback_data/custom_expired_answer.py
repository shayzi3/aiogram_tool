import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
     CallbackQuery,
     InlineKeyboardButton,
     InlineKeyboardMarkup,
     Message,
)
# Import base answer class
from aiogram_tool.tools.callback_data import LongCallbackData, CallbackDataAnswer

# Import memory lock storage
from aiogram_tool.storage.impl.memory import MemoryLockStorage


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Custom expired button answer
class MyExpiredAnswer(CallbackDataAnswer):
     async def __call__(self, query: CallbackQuery) -> None:
          # Send custom message instead of standard alert
          await query.message.answer(
               "Sorry, this button has expired. Please send /start again."
          )
          await query.answer()


class TempData(LongCallbackData, prefix="tmp"):
    _storage = MemoryLockStorage()
    _answer_callback = MyExpiredAnswer()  # Set custom answer
    
    operation_id: str
    huge_log: str


async def get_keyboard() -> InlineKeyboardMarkup:
     callback_data = await TempData(
          operation_id="op_123",
          huge_log="L" * 120
     ).pack_long()

     return InlineKeyboardMarkup(
          inline_keyboard=[
               [InlineKeyboardButton(text="Run operation", callback_data=callback_data)]
          ]
     )


@dp.message(CommandStart())
async def start_handler(message: Message):
     await message.answer(
          text="Keyboard created. Clear bot memory to see custom expired handler.",
          reply_markup=await get_keyboard(),
     )


@dp.callback_query(TempData.filter(F.operation_id == "op_123"))
async def process_operation(query: CallbackQuery, callback_data: TempData):
     await query.answer(text=f"Operation succeeded! Len huge log: {len(callback_data.huge_log)}")


async def main():
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())