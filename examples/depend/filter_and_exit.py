import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from aiogram_tool.tools.depend import DependExit, DependFilter, Depends, DependTool
from aiogram_tool.tools.setup import aiogram_tool_setup

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Dependency that checks user access. Raises DependExit to block execution
async def verify_user_access(context: Message) -> None:
    if context.from_user.id != 123456789:
        # Raising DependExit stops handler execution gracefully
        await context.answer("You are not admin!")
        raise DependExit()


@dp.message(
    CommandStart(),
    DependFilter(Depends(verify_user_access)),  # Filter runs dependency
)
async def start_handler(message: Message):
    # If we are here, verify_user_access didn't raise DependExit
    await message.answer("Welcome admin!")


# Also supported syntax
@dp.message(Command("other"))
async def other_handler(message: Message, test=Depends(verify_user_access)):
    # If we are here, verify_user_access didn't raise DependExit
    await message.answer("Welcome admin!")


async def main():
    depend_tool = DependTool()
    aiogram_tool_setup(dp, [depend_tool])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
