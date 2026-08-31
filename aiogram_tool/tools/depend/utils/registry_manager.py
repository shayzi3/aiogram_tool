from asyncio import Lock
from collections.abc import Callable, MutableMapping
from contextlib import nullcontext
from typing import Any, Self

from aiogram_tool.tools.depend.storage.memory import (
    DependencyMemoryLockStorage,
    DependencyMemoryStorage,
)
from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.types import _MISSING

MemoryStorageType = DependencyMemoryStorage | DependencyMemoryLockStorage


class DependRegistryTransaction:
    def __init__(self, app_storage: DependencyMemoryLockStorage) -> None:
        self.app_storage = app_storage
        self.storage = DependencyMemoryStorage()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        memory_storage: MutableMapping = self.storage.storage
        memory_storage.clear()

    def _get_storage(self, scope: Scope) -> MemoryStorageType | _MISSING:
        if scope == Scope.SINGLETON:
            return self.app_storage
        elif scope == Scope.REQUEST:
            return self.storage
        elif scope == Scope.TRANSIENT:
            return _MISSING

    def _get_lock_storage(self, scope: Scope) -> DependencyMemoryLockStorage | _MISSING:
        if scope == Scope.SINGLETON:
            return self.app_storage
        return _MISSING

    async def get_value(self, func: Callable, scope: Scope) -> Any | _MISSING:
        storage = self._get_storage(scope)
        if storage is not _MISSING:
            return await storage.get_value(key=func)
        return _MISSING

    async def set_value(self, func: Callable, scope: Scope, depend_result: Any) -> None:
        storage = self._get_storage(scope)
        if storage is not _MISSING:
            await storage.set_value(key=func, value=depend_result)

    async def lock(self, key: Callable, scope: Scope) -> Lock | nullcontext:
        storage = self._get_lock_storage(scope)
        if storage is not _MISSING:
            return await storage.lock(key=key)
        return nullcontext()


class DependRegistryTransactionManager:
    def __init__(self) -> None:
        self.storage = DependencyMemoryLockStorage()

    def transaction(self) -> DependRegistryTransaction:
        return DependRegistryTransaction(self.storage)
