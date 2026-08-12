import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from aiogram_tool.tools.depend import (
    Depends,
    DependTool,
    ScopeRegistry,
    Scope
)
from aiogram_tool.tools.setup import aiogram_tool_setup


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()

scope_registry = ScopeRegistry()


# Class-functor as a dependency
class CounterService:
    def __init__(self) -> None:
        self.count = 0

    async def __call__(self, context: Message) -> dict:
        self.count += 1
        return {
            "user_id": context.from_user.id,
            "current_count": self.count
        }


# You can pass an instance directly to Depends
counter_instance = CounterService()

# Register Scope for class-functor
scope_registry.register(counter_instance, Scope.REQUEST)


@dp.message(CommandStart())
async def start_handler(message: Message, stats: dict = Depends(counter_instance)):
    await message.answer(
        f"User ID: {stats['user_id']}\n"
        f"Button pressed: {stats['current_count']} times"
    )


# Also works with __init__ method
class BotToken:
    def __init__(self, bot: Bot) -> None:
        self.token = bot.token

# Register Scope for class
scope_registry.register(BotToken, Scope.SINGLETON)


@dp.message(Command("token"))
async def token_handler(
    message: Message, 
    bot_token: BotToken = Depends(BotToken)
):
    await message.answer(f"Bot token {bot_token.token}")


async def main():
    depend_tool = DependTool(scope_registry=scope_registry)
    aiogram_tool_setup(dp, [depend_tool])
     
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())