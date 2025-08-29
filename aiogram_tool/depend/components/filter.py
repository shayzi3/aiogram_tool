from contextlib import AsyncExitStack

from aiogram.filters import Filter
from aiogram.types.base import TelegramObject
from aiogram import Dispatcher
from aiogram.dispatcher.event.handler import HandlerObject

from .exit import DependExit
from ..depend import Depend
from ..utils.inject import inject_parametrs



class DependFilter(Filter):
     
     async def __call__(self, event: TelegramObject, **data):
          data.update({"event": event})
          
          dispatcher: Dispatcher = data.get("dispatcher")
          handler_object: HandlerObject = data.get("handler")
          
          dependency_override: dict[str, Depend] = dispatcher.get("dependency_override", {})
          stack: AsyncExitStack = data.get("async_stack")
          
          inject = await inject_parametrs(
               callback=handler_object.callback,
               dependency_override=dependency_override,
               middleware_data=data,
               stack=stack
          )
          for value in inject.values():
               if isinstance(value, DependExit):
                    await value.event_answer()
                    return False
          return inject