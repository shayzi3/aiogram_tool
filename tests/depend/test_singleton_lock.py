import asyncio

from aiogram_tool.tools.depend import ScopeRegistry, Scope, Depends, DependTool
from aiogram_tool.types import _MISSING
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction


async def test_singleton_lock(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     registry_transaction: DependRegistryTransaction,
     stack_transaction: AsyncExitStackTransaction
) -> None:
     
     class Test:
          ...
          
     @scope_registry(Scope.SINGLETON)
     async def depend(
          wait_time: int, 
          flag: bool, 
          depend_tool: DependTool
     ) -> Test:
          await asyncio.sleep(wait_time)
          value = await depend_tool.registry.storage.get_value(depend)
          assert value is _MISSING and flag is True
          return Test()
          
     async def handler(test: Test = Depends(depend)) -> None:
          assert isinstance(test, Test)
          
     middleware_data = (
          {"wait_time": 0.2, "flag": True, "depend_tool": depend_tool},
          {"wait_time": 0.01, "flag": False, "depend_tool": depend_tool}
     )
     resolver_first = DependResolver(
          handler_callback=handler,
          registry=registry_transaction,
          stack=stack_transaction,
          middleware_data=middleware_data[0],
          dependency_override={},
          scope_registry=scope_registry
     )
     resolver_second = DependResolver(
          handler_callback=handler,
          registry=registry_transaction,
          stack=stack_transaction,
          middleware_data=middleware_data[1],
          dependency_override={},
          scope_registry=scope_registry
     )
     await asyncio.gather(
          *[
               resolver_first.resolve_callback_depends(),
               resolver_second.resolve_callback_depends()
          ]
     )