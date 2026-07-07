from typing import Awaitable, Callable, Any, TYPE_CHECKING

from aiogram.types.base import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.components.exit import DependExit

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
          
          handler_callback: Callable = getattr(data.get("handler"), "callback")
          async with self.depend_tool.stack.transaction() as req_stack:
               async with self.depend_tool.registry.transaction() as req_registry:
                    resolver = DependResolver(
                         dependency_override=self.depend_tool.dependency_override,
                         handler_callback=handler_callback,
                         middleware_data=data,
                         registry=req_registry,
                         stack=req_stack
                    )
                    inject_params = await resolver.resolve_callback_depends()
                    for value in inject_params.values():
                         if isinstance(value, DependExit):
                              return await value.event_answer()
                    data.update(inject_params)
                    return await handler(event, data)