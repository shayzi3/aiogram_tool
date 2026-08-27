from typing import Any

from aiogram import Dispatcher
from aiogram.filters import Filter

from aiogram_tool.tools.depend.tool import DependTool
from aiogram_tool.tools.depend.depend import From

from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction
from aiogram_tool.tools.depend.types.exceptions import (
     InvalidDependencyError, 
     NotFoundDependTool
)
from .exit import DependExit



class DependFilter(Filter):
     """This class allows invoking a dependency at the filter level."""
     
     def __init__(self, *dependencies: From) -> None:
          for dep in dependencies:
               if not isinstance(dep, From):
                    raise InvalidDependencyError(f"Invalid type in dependency {dep}")
          
          self._dependencies = dependencies
          
     def get_depend_tool(self, data: dict[str, Any]) -> DependTool:
          dispatcher: Dispatcher = data.get("dispatcher")
          depend_tool = dispatcher.workflow_data.get("depend_tool")
          
          if not isinstance(depend_tool, DependTool):
               raise NotFoundDependTool(f"Not found DependTool. Add it in setup")
          return depend_tool
     
     def get_transactions(
          self, 
          data: dict[str, Any]
     ) -> tuple[DependRegistryTransaction, AsyncExitStackTransaction]:
          return data.get("request_registry"), data.get("request_stack")
          
     async def __call__(self, *args, **kwargs) -> bool:
          depend_tool = self.get_depend_tool(kwargs)
          req_registry, req_stack = self.get_transactions(kwargs)
          
          resolver = DependResolver(
               handler_callback=lambda: 1,
               registry=req_registry,
               stack=req_stack,
               scope_registry=depend_tool.scope_registry,
               middleware_data=kwargs.copy(),
               dependency_override=depend_tool.dependency_override
          )
          for depend in self._dependencies:
               scope_object = depend_tool.scope_registry.get_scope_object(depend)
               try:
                    params = await resolver.resolve_depend_params(
                         scope_object=scope_object,
                         resolved_depends=set()
                    )
                    await resolver.depend_call(
                         scope_object=scope_object,
                         params=params
                    )
               except DependExit:
                    return False
          return True
               
               
               
     