from typing import Any

from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.storage.base import BaseStorage

 


class AsyncRedisStorage(BaseStorage):
     
     def __init__(self, redis: AsyncRedis, expire: int | None = None) -> None:
          self.redis = redis
          self.expire = expire
          
     async def get_value(self, key: str, prefix: str) -> Any:
          key_with_prefix = self.build_key(key, prefix)
          return await self.redis.get(name=key_with_prefix)
               
     async def set_value(self, key: str, value: Any, prefix: str) -> None:
          key_with_prefix = self.build_key(key, prefix)
          await self.redis.set(name=key_with_prefix, value=value, ex=self.expire)
          
     