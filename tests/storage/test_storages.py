import asyncio
import secrets

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.types import _MISSING


async def test_storage(storage_lock: BaseLockStorage) -> None:
    storage_value = secrets.token_hex(50)

    value = await storage_lock.get_value(key=storage_value)
    assert value is _MISSING

    await storage_lock.set_value(key=storage_value, value="test_value")

    value = await storage_lock.get_value(key=storage_value)
    assert value == "test_value"

    async def increment() -> None:
        lock = await storage_lock.lock(key="test_lock_key")
        async with lock:
            value = await storage_lock.get_value(key="test_lock_key")
            if value is _MISSING:
                value = 0
            else:
                value = int(value)

            if value <= 2:
                await storage_lock.set_value(key="test_lock_key", value=value + 1)

    await asyncio.gather(*[increment(), increment()])
    value = await storage_lock.get_value(key="test_lock_key")
    assert int(value) == 2
