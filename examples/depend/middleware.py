import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters import CommandStart
from aiogram.types import Message, TelegramObject

from aiogram_tool.tools.depend import Depends, DependTool, Scope, ScopeRegistry
from aiogram_tool.tools.depend.utils.resolver import Resolver
from aiogram_tool.tools.setup import aiogram_tool_setup

bot = Bot("123456:TEST-PLACEHOLDER-TOKEN")
dp = Dispatcher()

scope_registry = ScopeRegistry()


class UserSession:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id


# REQUEST scope: one object per update, shared by middleware and handler
@scope_registry(Scope.REQUEST)
async def get_user_session(context: Message) -> UserSession:
    return UserSession(user_id=context.from_user.id)


class LoadUserSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Resolver is created by DependOuterMiddleware, so this middleware
        # must be registered after aiogram_tool_setup.
        # Since v1.2.7 middleware_data is passed per call — pass the
        # current `data` so the dependency can read middleware arguments
        resolver: Resolver = data["resolver"]
        data["user_session"] = await resolver.resolve(
            get_user_session, middleware_data=data
        )
        return await handler(event, data)


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    user_session: UserSession,
    session: UserSession = Depends(get_user_session),
):
    same = user_session is session
    await message.answer(
        f"User ID: {user_session.user_id}\nSame object in handler: {same}"
    )


async def main():
    depend_tool = DependTool(scope_registry=scope_registry)
    aiogram_tool_setup(dp, [depend_tool])
    dp.message.outer_middleware(LoadUserSessionMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
