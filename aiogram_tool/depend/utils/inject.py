import inspect

from contextlib import AsyncExitStack
from typing import (
     Any, 
     Callable, 
     _AnnotatedAlias 
)

from ..depend import Depend



async def depend_call(
     depend: Depend, 
     dependency_override: dict[str, Depend],
     middleware_data: dict[str, Any],
     stack: AsyncExitStack
) -> Any:
     call_object = depend
     if depend.obj_name in dependency_override.keys():
          call_object = dependency_override.get(depend.obj_name)
     return await call_object.call(middleware_data, stack)
          
     

async def inject_parametrs(
     callback: Callable,
     stack: AsyncExitStack,
     middleware_data: dict[str, Any],
     dependency_override: dict[str, Depend] = {},
) -> dict[str, Any]:
     injected_params = {}
     signature = inspect.signature(callback)
     for key, annotation in signature.parameters.items():
          default_value = annotation.default
               
          if isinstance(annotation.annotation, _AnnotatedAlias):
               types = getattr(annotation.annotation, "__metadata__")
               for dep in types:
                    if isinstance(dep, Depend):
                         injected_params[key] = await depend_call(
                              depend=dep,
                              dependency_override=dependency_override,
                              middleware_data=middleware_data,
                              stack=stack
                         )
                         
          elif isinstance(default_value, Depend):
               injected_params[key] = await depend_call(
                    depend=default_value,
                    dependency_override=dependency_override,
                    middleware_data=middleware_data,
                    stack=stack
               )
     return injected_params