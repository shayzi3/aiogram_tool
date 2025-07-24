from typing import Any
from contextlib import AsyncExitStack

from aiogram.filters import Filter
from aiogram import Dispatcher
from aiogram.dispatcher.event.handler import HandlerObject

from ..depend import Depend
from ..utils.inject import inject_parametrs




class DependFilter(Filter):
     
     
     async def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> dict[str, Any]:
          handler_object: HandlerObject = kwargs.get("handler")
          dispatcher: Dispatcher = kwargs.get("dispatcher")
          
          dependency_override: dict[str, Depend] = dispatcher.workflow_data.get("dependency_override", {})
          
          kwargs.update({"event": args[0]})
          async with AsyncExitStack() as stack:
               depend_kwargs = await inject_parametrs(
                    callback=handler_object.callback,
                    dependency_override=dependency_override,
                    middleware_data=kwargs,
                    stack=stack
               )
               return depend_kwargs