import asyncio

from typing import Annotated

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiotool.depend import (
    Depend,
    setup_depend_tool,
)



bot = Bot("TOKEN HERE")
dp = Dispatcher()



async def arguments(event: Message) -> str:
     await event.answer("Hello from Depend")
     return "all arguments"
     

@dp.message(CommandStart())
async def start(
     message: Message,
     arguments: Annotated[str, Depend(arguments)]
):
     await message.answer(arguments)  
     
     
async def main():
     setup_depend_tool(dispatcher=dp)
     await dp.start_polling(bot)
     
     
if __name__ == "__main__":
     asyncio.run(main())