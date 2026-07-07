import inspect

from typing import Any, Callable

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.schema import ScopeObject
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction
from aiogram_tool.tools.depend.utils.inspect import get_depends, extract_call_object


class DependResolver:
     
     def __init__(
          self, 
          handler_callback: Callable,
          registry: DependRegistryTransaction,
          stack: AsyncExitStackTransaction,
          middleware_data: dict[str, Any],
          dependency_override: dict[Callable, From]
     ) -> None:
          self.middleware_data = middleware_data
          self.dependency_override = dependency_override
          self.handler_callback = handler_callback
          self.registry = registry
          self.stack = stack
          
     async def resolve_callback_depends(self ) -> dict[str, Any]:
          handler_depends = get_depends(
               obj=self.handler_callback, 
               dependency_override=self.dependency_override
          )
          inject = {}
          for param_name, scope_object in handler_depends.items():
               resolved_depends = []
               
               depend_params = await self.resolve_depend_params(
                    scope_object=scope_object,
                    resolved_depends=resolved_depends
               )
               inject[param_name] = await self.depend_call(
                    scope_object=scope_object,
                    params=depend_params,
               )
          return inject
               
     async def resolve_depend_params(
          self, 
          scope_object: ScopeObject,
          resolved_depends: list[Callable]
     ) -> Any:
          if scope_object.depend in resolved_depends:
               raise RecursionError(f"Resursion detected {scope_object.depend}")
          resolved_depends.append(scope_object.depend)
          
          depend_params = {}
          
          subdepends = get_depends(
               obj=scope_object.depend,
               dependency_override=self.dependency_override
          )
          for subdepend_name, subdepend_scope in subdepends.items():
               subdepend_params = await self.resolve_depend_params(
                    scope_object=subdepend_scope,
                    resolved_depends=resolved_depends
               )
               depend_params[subdepend_name] = await self.depend_call(
                    scope_object=subdepend_scope,
                    params=subdepend_params,
               )
          
          params = inspect.signature(scope_object.depend)
          for param_name, param_meta in params.parameters.items():
               if param_name not in subdepends:
                    if (
                         param_name not in self.middleware_data
                         and param_meta.default is inspect._empty
                    ):
                         raise ValueError(f"Detect invalid argument {param_name} in {scope_object.depend}")
                    depend_params[param_name] = self.middleware_data.get(param_name)
          
          resolved_depends.pop()
          return depend_params
          
     
     async def depend_call(
          self,
          scope_object: ScopeObject,
          params: dict[str, Any],
     ) -> Any:
          cached = await self.registry.get_cached_depend(
               func=scope_object.depend,
               scope=scope_object.scope
          )
          if cached:
               return cached
               
          call_depend_object = extract_call_object(scope_object.depend)
          
          dependency_result = call_depend_object(**params)
          if inspect.isasyncgenfunction(call_depend_object):
               dependency_result = await self.stack.enter_async_context(
                    func=call_depend_object,
                    scope=scope_object.scope,
                    **params
               )
               
          elif inspect.isgeneratorfunction(call_depend_object):
               dependency_result = self.stack.enter_context(
                    func=call_depend_object,
                    scope=scope_object.scope,
                    **params
               )
               
          elif inspect.iscoroutinefunction(call_depend_object):
               dependency_result = await dependency_result
                    
          await self.registry.set_cached_depend(
               func=scope_object.depend,
               scope=scope_object.scope,
               depend_result=dependency_result
          )
          return dependency_result
     
     