

from aiogram_tool.tools.depend import DependTool, Depends, ScopeRegistry
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction



async def test_override_depends(
     depend_tool: DependTool,
     registry_transaction: DependRegistryTransaction,
     stack_transaction: AsyncExitStackTransaction,
     scope_registry: ScopeRegistry
) -> None:
     class TestDepend:
          def __init__(self):
               self.attr = "test"
               
     class TestDependOverride(TestDepend):
          def __init__(self):
               self.attr = "test_override"
     
     async def depend() -> int:
          return 10
     
     async def override_depend():
          return 3
     
     async def handler(
          integer: int = Depends(depend),
          test_depend: TestDepend = Depends(TestDepend)
     ) -> tuple[int, str]:
          return integer ** 2, "handler_" + test_depend.attr
     
     depend_tool.dependency_override = {
          depend: Depends(override_depend),
          TestDepend: Depends(TestDependOverride)
     }
     resolver = DependResolver(
          handler_callback=handler,
          registry=registry_transaction,
          stack=stack_transaction,
          scope_registry=scope_registry,
          middleware_data={},
          dependency_override=depend_tool.dependency_override
     )
     inject = await resolver.resolve_callback_depends()
     handler_result = await handler(**inject)
     assert handler_result == (9, "handler_test_override")
     