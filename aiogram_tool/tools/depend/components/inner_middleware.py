from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types.base import TelegramObject

from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction

from .exit import DependExit

if TYPE_CHECKING:
    from aiogram_tool.tools.depend.tool import DependTool


class DependInnerMiddleware(BaseMiddleware):
    """Class that injects dependencies into the handler"""

    def __init__(self, depend_tool: "DependTool") -> None:
        self.depend_tool = depend_tool

    def get_transactions(
        self, data: dict[str, Any]
    ) -> tuple[DependRegistryTransaction, AsyncExitStackTransaction]:
        return data.get("request_registry"), data.get("request_stack")

    def get_handler_callback(self, data: dict[str, Any]) -> Callable:
        return data["handler"].callback

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        handler_callback = self.get_handler_callback(data)
        req_registry, req_stack = self.get_transactions(data)

        resolver = DependResolver(
            dependency_override=self.depend_tool.dependency_override,
            scope_registry=self.depend_tool.scope_registry,
            handler_callback=handler_callback,
            registry=req_registry,
            stack=req_stack,
            middleware_data=data.copy(),
        )
        try:
            inject_params = await resolver.resolve_callback_depends()
        except DependExit:
            return

        data.update(inject_params)
        return await handler(event, data)
