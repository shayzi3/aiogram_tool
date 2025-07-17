from typing import Any, Callable, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher.event.handler import HandlerObject

from ..depend import Depend
from ..utils.inject import inject_parametrs





class DependMiddleware(BaseMiddleware):
          
          
     async def __call__(
          self, 
          handler: Callable[[Message, dict[str, Any]], Awaitable], 
          event: Message, 
          data: dict[str, Any]
     ):
          handler_object: HandlerObject = data.get("handler")
          dispatcher: Dispatcher = data.get("dispatcher")
          
          dependency_override: dict[str, Depend] = dispatcher.workflow_data.get("dependency_override", {})
          
          data.update({"event": event})
          inject = await inject_parametrs(
               callback=handler_object.callback,
               dependency_override=dependency_override,
               middleware_data=data
          )
          data.update(inject)
          return await handler(event, data)