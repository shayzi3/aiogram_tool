from typing import Awaitable, Callable, Any, TYPE_CHECKING

from aiogram.types.base import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from aiogram_tool.tools.depend.utils.resolver import DependResolver

if TYPE_CHECKING:
     from aiogram_tool.tools.depend.tool import DependTool
     


class DependInnerMiddleware(BaseMiddleware):
     
     def __init__(self, depend_tool: "DependTool") -> None:
          self.depend_tool = depend_tool
     
     async def __call__(
          self, 
          handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], 
          event: TelegramObject, 
          data: dict[str, Any]
     ) -> Any:
          data.update({"event": event})
          
          handler_callback: Callable = data["handler"].callback
          async with self.depend_tool.stack_manager.transaction() as req_stack:
               async with self.depend_tool.registry.transaction() as req_registry:
                    resolver = DependResolver(
                         dependency_override=self.depend_tool.dependency_override,
                         scope_registry=self.depend_tool.scope_registry,
                         handler_callback=handler_callback,
                         registry=req_registry,
                         stack=req_stack,
                         middleware_data=data.copy(),
                    )
                    inject_params = await resolver.resolve_callback_depends()
                    data.update(inject_params)
                    return await handler(event, data)