import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.types.base import TelegramObject
from aiogram.filters import CommandStart

from aiogram_tool.depend import (
    Depend,
    setup_depend_tool,
    DependFilter
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()


async def test_generator(event: TelegramObject):
     await event.message.answer("Hello from generator")
     yield 1


async def arguments(event: TelegramObject, num: Annotated[int, Depend(test_generator)]) -> str:
     await event.answer(f"Hello from DependFilter. Num: {num}")  
     return "Hello!"   
     

@dp.message(CommandStart(), DependFilter())
async def start(
     message: Message,
     arguments: Annotated[str, Depend(arguments)]
):
     await message.answer(arguments)  
     
     
async def main():
     setup_depend_tool(dispatcher=dp, middleware=False)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())