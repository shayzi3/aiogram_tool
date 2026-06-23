from typing import Dict, Any, Callable, _AnnotatedAlias, Optional, Union
from contextlib import AsyncExitStack

from aiogram_tool.tools.depend.depend import Depends
from aiogram_tool.utils.inspect_signature import InspectSignature
from aiogram_tool.storage import MemoryLimitStorage, MemoryStorage
from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.utils.types_ import UNSET


class DependResolver:
     
     def __init__(
          self, 
          storage: Union[MemoryStorage, MemoryLimitStorage],
          cache_prefix: str,
          handler_callback: Optional[Callable] = None
     ) -> None:
          self.signature = None
          if handler_callback:
               self.signature = InspectSignature(handler_callback)
               
          self.storage = storage
          self.cache_prefix = cache_prefix
          
          
     async def resolve(
          self, 
          middleware_data: Dict[str, Any], 
          dependency_override: Optional[Dict[str, Depends]],
          stack: AsyncExitStack,
          signature: Optional[InspectSignature] = None,
          inject_only_depends: bool = True
     ) -> Dict[str, Any]:
          if signature is None:
               signature = self.signature
               
          inject = {}
          for key, type_hint in signature.type_hints_with_default.items():
               default = type_hint.default
               
               if isinstance(type_hint.annotation, _AnnotatedAlias):
                    metas = getattr(type_hint.annotation, "__metadata__")
                    for dep in metas:
                         if isinstance(dep, Depends):
                              inject[key] = await self.depend_call(
                                   depend=dep,
                                   dependency_override=dependency_override,
                                   middleware_data=middleware_data,
                                   stack=stack
                              )

               elif isinstance(default, Depends):
                    inject[key] = await self.depend_call(
                         depend=default,
                         dependency_override=dependency_override,
                         middleware_data=middleware_data,
                         stack=stack
                    )
               
               else:
                    if inject_only_depends is False:
                         if key in middleware_data.keys():
                              inject[key] = middleware_data[key]
                         else:
                              if default is UNSET:
                                   raise ValueError(
                                        (
                                             f"Argument {key} in {signature.obj} invalid. "
                                             "Not found in middleware data and not default value."
                                        )
                                   )
          return inject
     
     
     async def depend_call(
          self,
          depend: Depends,
          stack: AsyncExitStack,
          dependency_override: Optional[Dict[str, Depends]],
          middleware_data: Dict[str, Any]
     ) -> Any:
          if dependency_override:
               if depend.signature.obj_name in dependency_override.keys():
                    depend = dependency_override.get(depend.signature.obj_name)
               
          if depend.scope == Scope.APP:
               cached = await self.storage.get_value(
                    key=hash(depend),
                    prefix=self.cache_prefix
               )
               if cached:
                    return cached
               
          dependency_params = await self.resolve(
               middleware_data=middleware_data,
               dependency_override=dependency_override,
               stack=stack,
               inject_only_depends=False,
               signature=depend.signature
          )
          dependency_result = depend.signature.obj(**dependency_params)
          if depend.signature.is_async:
               if depend.signature.is_generator:
                    dependency_result = await stack.enter_async_context(dependency_result)
               else:
                    dependency_result = await dependency_result
          else:
               if depend.signature.is_generator:
                    dependency_result = stack.enter_context(dependency_result)
                    
          if depend.scope == Scope.APP:
               await self.storage.set_value(
                    key=hash(depend),
                    value=dependency_result,
                    prefix=self.cache_prefix
               )
          return dependency_result