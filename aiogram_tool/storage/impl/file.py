import os
from asyncio import Lock
from collections.abc import MutableMapping

import aiofiles

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.types import _MISSING


class FileStorage(MemoryStorage):
    def __init__(self, file: str, storage: MutableMapping | None = None) -> None:
        if not os.path.exists(file):
            raise FileNotFoundError(f"File {file} not found")

        self.file = file

        self._is_memory = False
        if storage is not None:
            self._is_memory = True
            super().__init__(storage=storage)

    async def set_value(self, key: str, value: str) -> None:
        if "&" in key:
            raise ValueError(f"Symbol & can't use in key {key}")

        async with aiofiles.open(self.file, "a") as aiofile:
            await aiofile.write(f"\n{key}&{value}")

        if self._is_memory:
            await super().set_value(key=key, value=value)

    async def get_value(self, key: str) -> str | _MISSING:
        if self._is_memory:
            value = await super().get_value(key=key)
            if value:
                return value

        async with aiofiles.open(self.file) as aiofile:
            data = await aiofile.readlines()
            data.reverse()

        for line in data:
            line = line.strip()
            if not line:
                continue

            line_key, line_value = line.split(sep="&", maxsplit=1)
            if line_key == key:
                if self._is_memory:
                    await super().set_value(key, line_value)
                return line_value
        return _MISSING


class FileLockStorage(FileStorage, BaseLockStorage):
    def __init__(
        self,
        file: str,
        storage: MutableMapping | None = None,
        locks_storage: MutableMapping | None = None,
    ) -> None:
        self.global_lock = Lock()
        self.locks = locks_storage if locks_storage is not None else {}
        super().__init__(file=file, storage=storage)

    async def lock(self, key: str) -> Lock:
        async with self.global_lock:
            if key not in self.locks.keys():
                self.locks[key] = Lock()
            return self.locks[key]
