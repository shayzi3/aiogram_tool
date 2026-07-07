from contextlib import AsyncExitStack

from aiogram import Dispatcher
from aiogram.filters import Filter
from aiogram.types.base import TelegramObject

from aiogram_tool.tools.depend.tool import DependTool
from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from .exit import DependExit



class DependHandler(Filter):
     __slots__ = ("__dependencies",)
     
     def __init__(self, *dependencies: From) -> None:
          for dep in dependencies:
               if not isinstance(dep, From):
                    raise TypeError("Invalid type in dependency")
          
          self.__dependencies = dependencies
          
     async def __call__(
          self, 
          event: TelegramObject, 
          dispatcher: Dispatcher,
          **kwargs
     ) -> bool:
          kwargs.update({"event": event})
          
          depend_tool: DependTool = dispatcher.workflow_data.get("dependency_tool", None)
          
          if not isinstance(depend_tool, DependTool):
               raise ValueError(f"Not found DependTool. Add it in setup")
          
          async with AsyncExitStack() as stack:
               resolver = DependResolver(storage=depend_tool.storage)
               
               for depend in self.__dependencies:
                    result = await resolver.depend_call(
                         depend=depend,
                         stack=stack,
                         dependency_override=depend_tool.dependency_override,
                         middleware_data=kwargs
                    )
                    if isinstance(result, DependExit):
                         await result.event_answer()
                         return False
          return True
               
               
               
     