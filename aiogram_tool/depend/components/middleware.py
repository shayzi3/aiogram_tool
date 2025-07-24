from typing import Any, Callable, Awaitable
from contextlib import AsyncExitStack

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types.base import TelegramObject
from aiogram import Dispatcher
from aiogram.dispatcher.event.handler import HandlerObject

from ..depend import Depend
from ..utils.inject import inject_parametrs





class DependMiddleware(BaseMiddleware):
          
          
     async def __call__(
          self, 
          handler: Callable[[TelegramObject, dict[str, Any]], Awaitable], 
          event: TelegramObject, 
          data: dict[str, Any]
     ):
          handler_object: HandlerObject = data.get("handler")
          dispatcher: Dispatcher = data.get("dispatcher")
          
          dependency_override: dict[str, Depend] = dispatcher.workflow_data.get("dependency_override", {})
          
          data.update({"event": event})
          async with AsyncExitStack() as stack:
               inject = await inject_parametrs(
                    callback=handler_object.callback,
                    dependency_override=dependency_override,
                    middleware_data=data,
                    stack=stack
               )
               data.update(inject)
               return await handler(event, data)