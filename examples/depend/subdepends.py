import asyncio

from typing import Annotated

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Import Depends and setup tools
from aiogram_tool.tools.depend import (
     DependTool,
     Depends,
)
from aiogram_tool.tools.setup import aiogram_tool_setup


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Sub-dependency: provides database session
async def get_db_session():
     yield "DB_SESSION"


# Main dependency: requires db_session, gets context from middleware data
async def get_user_message(
     context: Message, 
     db_session: str = Depends(get_db_session)
):
     return f"{context.from_user.username} session for you {db_session}"


@dp.message(CommandStart())
async def start_handler(
     message: Message, 
     user_message: Annotated[str, Depends(get_user_message)]
):
    await message.answer(user_message)


async def main():
     # Initialize and setup DependTool
     depend_tool = DependTool()
     aiogram_tool_setup(dp, [depend_tool])
     
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())