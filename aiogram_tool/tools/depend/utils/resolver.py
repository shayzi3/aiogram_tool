import inspect

from typing import Any, Callable
from contextlib import (
     AbstractAsyncContextManager, 
     AbstractContextManager,
     asynccontextmanager,
)

from aiogram_tool.tools.depend.types.exceptions import (
     DependRecursionError,
     UnsupportedParameterKindError,
     InvalidMiddlewareDataArgumentError,
     ContextManagerError
)
from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.schema import ScopeObject
from aiogram_tool.tools.depend.utils.scope_registry import ScopeRegistry
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction
from aiogram_tool.types import _MISSING
from aiogram_tool.tools.depend.utils.inspect import get_arguments


class DependResolver:
     
     def __init__(
          self, 
          handler_callback: Callable,
          registry: DependRegistryTransaction,
          stack: AsyncExitStackTransaction,
          scope_registry: ScopeRegistry,
          middleware_data: dict[str, Any],
          dependency_override: dict[Callable, From],
     ) -> None:
          self.middleware_data = middleware_data
          self.scope_registry = scope_registry
          self.dependency_override = dependency_override
          self.handler_callback = handler_callback
          self.registry = registry
          self.stack = stack
          
     async def resolve_callback_depends(self ) -> dict[str, Any]:
          arguments = get_arguments(
               obj=self.handler_callback, 
               scope_registry=self.scope_registry,
               dependency_override=self.dependency_override,
          )
          inject = {}
          for arg_meta in arguments:
               if isinstance(arg_meta.value, ScopeObject):
                    depend_params = await self.resolve_depend_params(
                         scope_object=arg_meta.value,
                         resolved_depends=set()
                    )
                    inject[arg_meta.name] = await self.depend_call(
                         scope_object=arg_meta.value,
                         params=depend_params,
                    )
          return inject
               
     async def resolve_depend_params(
          self, 
          scope_object: ScopeObject,
          resolved_depends: set[Callable]
     ) -> Any:
          if scope_object.depend in resolved_depends:
               raise DependRecursionError(
                    f"Recursion detected {scope_object.depend}"
                    f" chain of dependencies {resolved_depends}"
               )
          resolved_depends.add(scope_object.depend)
          
          depend_params = {}
          
          arguments = get_arguments(
               obj=scope_object.depend,
               scope_registry=self.scope_registry,
               dependency_override=self.dependency_override,
          )
          for arg_meta in arguments:
               if isinstance(arg_meta.value, ScopeObject):
                    subdepend_params = await self.resolve_depend_params(
                         scope_object=arg_meta.value,
                         resolved_depends=resolved_depends
                    )
                    depend_params[arg_meta.name] = await self.depend_call(
                         scope_object=arg_meta.value,
                         params=subdepend_params,
                    )
               else:
                    if arg_meta.arg_kind in [
                         inspect.Parameter.POSITIONAL_ONLY,
                         inspect.Parameter.VAR_KEYWORD,
                         inspect.Parameter.VAR_POSITIONAL
                    ]:
                         raise UnsupportedParameterKindError(
                              f"Dont support parameter type {arg_meta.arg_kind} in"
                              f" {scope_object.depend}, param {arg_meta.name}"
                         )
                    
                    if arg_meta.value is inspect.Signature.empty:
                         middleware_data_value = self.middleware_data.get(arg_meta.name, _MISSING)
                         if middleware_data_value is _MISSING:
                              raise InvalidMiddlewareDataArgumentError(
                                   f"Detect invalid argument {arg_meta.name} in {scope_object.depend}"
                              )
                         depend_params[arg_meta.name] = middleware_data_value
                    else:
                         middleware_data_value = self.middleware_data.get(arg_meta.name, arg_meta.value)
                         depend_params[arg_meta.name] = middleware_data_value
                    
          resolved_depends.remove(scope_object.depend)
          return depend_params
          
     
     async def depend_call(
          self,
          scope_object: ScopeObject,
          params: dict[str, Any],
     ) -> Any:
          lock = await self.registry.lock(
               key=scope_object.depend,
               scope=scope_object.scope
          )
          async with lock:
               cached = await self.registry.get_value(
                    func=scope_object.depend,
                    scope=scope_object.scope
               )
               if cached is not _MISSING:
                    return cached
               
               dependency_result = None
               if inspect.isgeneratorfunction(scope_object.depend):
                    raise ContextManagerError(
                         "Only async dependencies are supported."
                         " Use async def or @asynccontextmanager."
                    )
               
               elif inspect.isasyncgenfunction(scope_object.depend):
                    cm = asynccontextmanager(scope_object.depend)(**params)
                    dependency_result = await self.stack.enter_async_context(
                         context_manager=cm,
                         scope=scope_object.scope
                    )
               else:
                    dependency_result = scope_object.depend(**params)
                    if inspect.isawaitable(dependency_result):
                         dependency_result = await dependency_result 

                    elif isinstance(dependency_result, AbstractAsyncContextManager):
                         dependency_result = await self.stack.enter_async_context(
                              context_manager=dependency_result,
                              scope=scope_object.scope
                         )

                    elif isinstance(dependency_result, AbstractContextManager):
                         raise ContextManagerError(
                              "Only async dependencies are supported."
                              " Use async def or @asynccontextmanager."
                         )
               
               await self.registry.set_value(
                    func=scope_object.depend,
                    scope=scope_object.scope,
                    depend_result=dependency_result
               )
          return dependency_result