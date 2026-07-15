import pytest

from aiogram_tool.tools.depend.tool import DependTool
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransaction
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction


@pytest.fixture(scope="session")
def depend_tool() -> DependTool:
     return DependTool()

@pytest.fixture(scope="function")
async def registry_transaction(depend_tool: DependTool):
     async with depend_tool.registry.transaction() as transaction:
          yield transaction
          
@pytest.fixture(scope="function")
async def stack_transaction(depend_tool: DependTool):
     async with depend_tool.stack.transaction() as transaction:
          yield transaction
          
@pytest.fixture(scope="function")
async def depend_resolver(
     registry_transaction: DependRegistryTransaction,
     stack_transaction: AsyncExitStackTransaction,
) -> DependResolver:
     return DependResolver(
          handler_callback=lambda: 1,
          registry=registry_transaction,
          stack=stack_transaction,
          middleware_data={},
          dependency_override={}
     )