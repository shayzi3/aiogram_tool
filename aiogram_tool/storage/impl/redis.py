from typing import Any

from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.lock import Lock as RedisLock

from aiogram_tool.storage.base import BaseStorage, BaseLockStorage
from aiogram_tool.types import _MISSING

 

class AsyncRedisStorage(BaseStorage):
     
     def __init__(
          self, 
          redis: AsyncRedis, 
          expire: int | None = None
     ) -> None:
          self.redis = redis
          self.expire = expire
          
     async def get_value(self, key: str) -> Any:
          value = await self.redis.get(name=key)
          return value if value else _MISSING
               
     async def set_value(self, key: str, value: Any) -> None:
          await self.redis.set(name=key, value=value, ex=self.expire)
          

     
class AsyncRedisLockStorage(AsyncRedisStorage, BaseLockStorage):
     
     def __init__(
          self, 
          redis: AsyncRedis, 
          expire: int | None = None,
     ) -> None:
          super().__init__(
               redis=redis,
               expire=expire
          )
          
     async def lock(self, key: str) -> RedisLock:
          return self.redis.lock(
               name=key,
               timeout=10,
               blocking_timeout=20
          )
               