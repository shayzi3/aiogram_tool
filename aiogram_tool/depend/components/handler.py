from contextlib import AsyncExitStack
from aiogram.filters import Filter
from aiogram.types.base import TelegramObject

from ..depend import Depend
from .exit import DependExit



class DependHandler(Filter):
     def __init__(self, *dependencies: Depend):
          for dep in dependencies:
               if not isinstance(dep, Depend):
                    raise TypeError("Invalid type in dependency")
          
          self._dependencies = dependencies
             
          
     async def __call__(self, event: TelegramObject, **kwargs) -> bool:
          kwargs.update({"event": event})
          
          async with AsyncExitStack() as stack:
               for depend in self._dependencies:
                    result = await depend.call(
                         middleware_data=kwargs,
                         stack=stack
                    )
                    if isinstance(result, DependExit):
                         await result.event_answer()
                         return False
          return True
               
               
               
     