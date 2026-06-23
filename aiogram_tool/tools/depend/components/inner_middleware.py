from typing import Awaitable, Callable, Any, Dict
from contextlib import AsyncExitStack

from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types.base import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from aiogram_tool.tools.depend.tool import DependTool
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.components.exit import DependExit


class DependInnerMiddleware(BaseMiddleware):
     
     def __init__(self, depend_tool: DependTool) -> None:
          self.depend_tool = depend_tool
          
     async def __call__(
          self, 
          handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], 
          event: TelegramObject, 
          data: Dict[str, Any]
     ) -> Any:
          data.update({"event": event})
          
          handler_: HandlerObject = data.get("handler")
          async with AsyncExitStack() as stack: 
               resolver = DependResolver(
                    handler_callback=handler_.callback,
                    cache_prefix=self.depend_tool.tool,
                    storage=self.depend_tool.storage
               )  
               inject_params = await resolver.resolve(
                    middleware_data=data,
                    dependency_override=self.depend_tool.dependency_override,
                    stack=stack
               )
               for value in inject_params.values():
                    if isinstance(value, DependExit):
                         return await value.event_answer()

               data.update(inject_params)
               return await handler(event, data)