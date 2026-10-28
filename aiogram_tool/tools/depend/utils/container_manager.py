from collections.abc import Callable
from typing import Self

from aiogram_tool.tools.depend.depend import From

from .registry_manager import (
    DependRegistryTransaction,
    DependRegistryTransactionManager,
)
from .scope_registry import ScopeRegistry
from .stack_manager import AsyncExitStackTransaction, AsyncExitStackTransactionManager


class ContainerTransaction:
    def __init__(
        self,
        manager: "ContainerManager",
        registry_transaction: DependRegistryTransaction,
        stack_transaction: AsyncExitStackTransaction,
    ) -> None:
        self.manager = manager
        self.registry_transaction = registry_transaction
        self.stack_transaction = stack_transaction

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.registry_transaction.close()
        await self.stack_transaction.close(*args)


class ContainerManager:
    def __init__(
        self,
        scope_registry: ScopeRegistry | None = None,
        dependency_override: dict[Callable, From] | None = None,
    ) -> None:
        self.scope_registry = scope_registry or ScopeRegistry()
        self.dependency_override = dependency_override or {}
        self.registry = DependRegistryTransactionManager()
        self.stack_manager = AsyncExitStackTransactionManager()

    def transaction(self) -> ContainerTransaction:
        return ContainerTransaction(
            manager=self,
            registry_transaction=self.registry.transaction(),
            stack_transaction=self.stack_manager.transaction(),
        )

    async def shutdown(self) -> None:
        await self.stack_manager.stack.aclose()
