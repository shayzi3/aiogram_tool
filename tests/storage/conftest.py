import os
import pytest

from typing import AsyncGenerator

from redis.asyncio import Redis

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.storage import (
     MemoryLockStorage,
     FileLockStorage,
     AsyncRedisLockStorage
)
          
          
@pytest.fixture(
     scope="function",
     params=[
          MemoryLockStorage,
          FileLockStorage, 
          AsyncRedisLockStorage
     ]
)
async def storage_lock(request) -> AsyncGenerator[BaseLockStorage, None]:
     instance = None
     param = request.param
     
     if param is FileLockStorage:
          with open("./test.txt", "w"): ...
          instance = param(file="./test.txt")
          
     elif param is AsyncRedisLockStorage:
          instance = param(redis=Redis(protocol=2), expire=60)
     
     else:
          instance = param()
     
     yield instance
     
     if isinstance(instance, FileLockStorage):
          os.remove("./test.txt")
     
     elif isinstance(instance, AsyncRedisLockStorage):
          await instance.redis.aclose()