from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject

from aiogram_tool.tools.depend.utils.container_manager import ContainerManager
from aiogram_tool.tools.depend.utils.resolver import Resolver


class DependOuterMiddleware(BaseMiddleware):
    def __init__(self, container_manager: ContainerManager) -> None:
        self.container_manager = container_manager

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["context"] = event
        async with self.container_manager.transaction() as container_transaction:
            data["resolver"] = Resolver(container_transaction=container_transaction)
            return await handler(event, data)
