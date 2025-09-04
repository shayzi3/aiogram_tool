from typing import Awaitable, Callable, Any
from contextlib import AsyncExitStack

from aiogram import Dispatcher
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types.base import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from .exit import DependExit
from ..depend import Depend
from ..utils.inject_callback import inject_parametrs



class DependInnerMiddleware(BaseMiddleware):
     
     async def __call__(
          self, 
          handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], 
          event: TelegramObject, 
          data: dict[str, Any]
     ) -> Any:
          data.update({"event": event})
          
          dispatcher: Dispatcher = data.get("dispatcher")
          handler_object: HandlerObject = data.get("handler")
          
          dependency_override: dict[str, Depend] = dispatcher.get("dependency_override", {})

          async with AsyncExitStack() as stack:   
               inject = await inject_parametrs(
                    callback=handler_object.callback,
                    dependency_override=dependency_override,
                    middleware_data=data,
                    stack=stack
               )
               for value in inject.values():
                    if isinstance(value, DependExit):
                         return await value.event_answer()

               data.update(inject)
               return await handler(event, data)