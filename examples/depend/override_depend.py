import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command

from aiogram_tool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()


async def depend_one() -> str:
     return "Function One"


async def depend_two() -> str:
     return "Function Two"



@dp.message(Command("start_one"))
async def start_one(
     message: Message,
     text: Annotated[str, Depend(depend_one)]
):
     assert "Two" in text
     await message.answer(text)
     


@dp.message(Command("start_two"))
async def start_two(
     message: Message,
     text: Annotated[str, Depend(depend_two)]
):
     assert "One" in text
     await message.answer(text)

     
     
async def main():
     override = {
          "depend_one": Depend(depend_two),
          "depend_two": Depend(depend_one)
     }
     setup_depend_tool(dispatcher=dp, dependency_override=override)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())