from asyncio import Lock
from collections.abc import Callable, MutableMapping
from typing import Any

from aiogram_tool.types import _MISSING


class DependencyMemoryStorage:
    def __init__(self) -> None:
        self.storage: MutableMapping = {}

    async def get_value(self, key: Callable) -> Any | _MISSING:
        return self.storage.get(key, _MISSING)

    async def set_value(self, key: Callable, value: Any) -> None:
        self.storage[key] = value


class DependencyMemoryLockStorage(DependencyMemoryStorage):
    def __init__(self):
        self.global_lock = Lock()
        self.locks: MutableMapping = {}
        super().__init__()

    async def lock(self, key: Callable) -> Lock:
        async with self.global_lock:
            if key not in self.locks.keys():
                self.locks[key] = Lock()
            return self.locks[key]
