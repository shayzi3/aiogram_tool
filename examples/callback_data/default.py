import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_tool.callback_data import LongCallbackData


bot = Bot("TOKEN HERE")
dp = Dispatcher()



class SomeData(LongCallbackData, prefix="&"):
     mode: str
     data: str
     

inline = InlineKeyboardMarkup(
     inline_keyboard=[
          [
               InlineKeyboardButton(
                    text="Some Text 1",
                    callback_data=SomeData(
                         mode="some_data_1",
                         data="Hi, today I was walking along."
                    ).pack() # not error `callback data too long`
               )
          ],
          [
               InlineKeyboardButton(
                    text="Some Text 2",
                    callback_data=SomeData(
                         mode="some_data_2",
                         data="VEEEEEEEEEEEEEEEEEEEEEEEEEEERY LOOOOOOOOOOOOOOOOOOOOONG DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATA"
                    ).pack()
               )
          ]
     ]
)


@dp.message(CommandStart())
async def start(
     message: Message
):
     await message.answer(
          text="Buttons",
          reply_markup=inline
     )

     
@dp.callback_query(SomeData.filter(F.mode == "some_data_1"))
async def some_data_one(
     query: CallbackQuery,
     callback_data: SomeData
):
     await query.answer(text=callback_data.data)
     
     
@dp.callback_query(SomeData.filter(F.mode == "some_data_2"))
async def some_data_2(
     query: CallbackQuery,
     callback_data: SomeData
):
     await query.answer(text=callback_data.data)
     
     
     
async def main() -> None:
     await dp.start_polling(bot)
     
     
     
if __name__ == "__main__":
     asyncio.run(main())