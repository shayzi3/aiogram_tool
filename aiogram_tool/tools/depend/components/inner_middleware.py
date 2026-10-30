from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types.base import TelegramObject

from aiogram_tool.tools.depend.utils.resolver import Resolver

from .exit import DependExit


class DependInnerMiddleware(BaseMiddleware):
    """Class that injects dependencies into the handler"""

    def _get_resolver(self, data: dict[str, Any]) -> Resolver:
        if "resolver" not in data:
            raise ValueError("Resolver not found in data")
        return data["resolver"]

    def _get_handler_callback(self, data: dict[str, Any]) -> Callable:
        if "handler" not in data:
            raise ValueError("Handler not found in data")
        return data["handler"].callback

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        resolver = self._get_resolver(data)
        try:
            inject_params = await resolver.resolve_handler(
                handler=self._get_handler_callback(data), middleware_data=data
            )
        except DependExit:
            return

        data.update(inject_params)
        return await handler(event, data)
