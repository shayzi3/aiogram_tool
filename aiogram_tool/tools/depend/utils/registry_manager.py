from asyncio import Lock
from collections.abc import Callable, MutableMapping
from contextlib import nullcontext
from typing import Any

from aiogram_tool.tools.depend.storage.memory import (
    DependencyMemoryLockStorage,
    DependencyMemoryStorage,
)
from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.types import _MISSING, _MissingType

MemoryStorageType = DependencyMemoryStorage | DependencyMemoryLockStorage


class DependRegistryTransaction:
    def __init__(self, app_storage: DependencyMemoryLockStorage) -> None:
        self.app_storage = app_storage
        self.storage = DependencyMemoryStorage()

    async def close(self) -> None:
        memory_storage: MutableMapping = self.storage.storage
        memory_storage.clear()

    def _get_storage(self, scope: Scope) -> MemoryStorageType | _MissingType:
        if scope == Scope.SINGLETON:
            return self.app_storage
        elif scope == Scope.REQUEST:
            return self.storage
        elif scope == Scope.TRANSIENT:
            return _MISSING

    def _get_lock_storage(
        self, scope: Scope
    ) -> DependencyMemoryLockStorage | _MissingType:
        if scope == Scope.SINGLETON:
            return self.app_storage
        return _MISSING

    async def get_value(self, func: Callable, scope: Scope) -> Any | _MissingType:
        storage = self._get_storage(scope)
        if not isinstance(storage, _MissingType):
            return await storage.get_value(key=func)
        return _MISSING

    async def set_value(self, func: Callable, scope: Scope, depend_result: Any) -> None:
        storage = self._get_storage(scope)
        if not isinstance(storage, _MissingType):
            await storage.set_value(key=func, value=depend_result)

    async def lock(self, key: Callable, scope: Scope) -> Lock | nullcontext:
        storage = self._get_lock_storage(scope)
        if not isinstance(storage, _MissingType):
            return await storage.lock(key=key)
        return nullcontext()


class DependRegistryTransactionManager:
    def __init__(self) -> None:
        self.storage = DependencyMemoryLockStorage()

    def transaction(self) -> DependRegistryTransaction:
        return DependRegistryTransaction(self.storage)
