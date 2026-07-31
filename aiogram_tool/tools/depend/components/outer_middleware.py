from typing import Callable, Any, Awaitable, TYPE_CHECKING

from aiogram.types import TelegramObject

from aiogram.dispatcher.middlewares.base import BaseMiddleware

if TYPE_CHECKING:
     from aiogram_tool.tools.depend.tool import DependTool



class DependOuterMiddleware(BaseMiddleware):
     
     def __init__(self, depend_tool: "DependTool") -> None:
          self.depend_tool = depend_tool
     
     async def __call__(
         self,
         handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
         event: TelegramObject,
         data: dict[str, Any]
     ) -> Any:
          data["context"] = event
          async with self.depend_tool.registry.transaction() as req_registry:
               async with self.depend_tool.stack_manager.transaction() as req_stack:
                    data.update(
                         {
                              "request_registry": req_registry,
                              "request_stack": req_stack
                         }
                    )
                    return await handler(event, data)