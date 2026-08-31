import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_tool.tools.depend import Depends, DependTool
from aiogram_tool.tools.setup import aiogram_tool_setup

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Real dependency (e.g., makes API call)
async def get_external_data():
    return "REAL_API_DATA"


# Mock dependency for testing or local dev
async def get_mocked_data():
    return "MOCKED_DATA"


@dp.message(CommandStart())
async def start_handler(message: Message, data: str = Depends(get_external_data)):
    # Will use MOCKED_DATA because of the override
    await message.answer(f"Data received: {data}")


async def main():
    # Setup DependTool with dependency_override
    depend_tool = DependTool(
        dependency_override={get_external_data: Depends(get_mocked_data)}
    )
    aiogram_tool_setup(dp, [depend_tool])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
