from datetime import datetime
from redis.asyncio import Redis as AsyncRedis


from .abstract_storage import AbstractStorage




class RedisStorage(AbstractStorage):
     def __init__(self, redis: AsyncRedis):
          if not isinstance(redis, AsyncRedis):
               raise TypeError("Invalid type for redis")
          
          self._redis = redis
          
          
     async def get(self, name: str) -> datetime | None:
          async with self._redis as session:
               data = await session.hget(name="limit_tool", key=name)
               if data is None:
                    return None
               
               if isinstance(data, bytes):
                    data = data.decode()
          return datetime.fromisoformat(data)
     
          
     async def update(self, name: str, value: datetime) -> None:
          async with self._redis as session:
               await session.hset(
                    name="limit_tool",
                    key=name,
                    value=value.isoformat()
               )