import inspect

from typing import Any, Callable, _AnnotatedAlias

from ..depend import Depend



async def inject_parametrs(
     callback: Callable,
     middleware_data: dict[str, Any],
     dependency_override: dict[str, Depend] = {},
) -> dict[str, Any]:
     data = {}
     signature = inspect.signature(callback)
     for key, annotation in signature.parameters.items():
          default_value = annotation.default
               
          if isinstance(annotation.annotation, _AnnotatedAlias):
               types = getattr(annotation.annotation, "__metadata__")
               for type_ in types:
                    if isinstance(type_, Depend):
                         if type_.obj_name in dependency_override.keys():
                              data[key] = await dependency_override[type_.obj_name].call(middleware_data)
                         else:
                              data[key] = await type_.call(middleware_data)
               
          elif isinstance(default_value, Depend):
               if default_value.obj_name in dependency_override.keys():
                    data[key] = await dependency_override[default_value.obj_name].call(middleware_data)
               else:
                    data[key] = await default_value.call(middleware_data)
     return data