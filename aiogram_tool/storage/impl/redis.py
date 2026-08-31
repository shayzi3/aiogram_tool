from typing import Any

from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.lock import Lock as RedisLock

from aiogram_tool.storage.base import BaseLockStorage, BaseStorage
from aiogram_tool.types import _MISSING


class AsyncRedisStorage(BaseStorage):
    def __init__(self, redis: AsyncRedis, expire: int | None = None) -> None:
        self.redis = redis
        self.expire = expire

    async def get_value(self, key: str) -> str | _MISSING:
        value = await self.redis.get(name=key)
        if value is not None:
            return value.decode() if isinstance(value, bytes) else value
        return _MISSING

    async def set_value(self, key: str, value: Any) -> None:
        await self.redis.set(name=key, value=value, ex=self.expire)


class AsyncRedisLockStorage(AsyncRedisStorage, BaseLockStorage):
    def __init__(
        self,
        redis: AsyncRedis,
        expire: int | None = None,
    ) -> None:
        super().__init__(redis=redis, expire=expire)

    async def lock(self, key: str) -> RedisLock:
        lock_key = f"aigram_tool_lock:{key}"
        return self.redis.lock(
            name=lock_key,
            timeout=10,
            blocking_timeout=10,
        )
