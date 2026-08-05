import os
import pytest

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from redis.asyncio import Redis

from aiogram_tool.storage.base import BaseLockStorage, BaseStorage
from aiogram_tool.storage import (
     MemoryLockStorage,
     FileLockStorage,
     AsyncRedisLockStorage,
     MemoryStorage,
     FileStorage,
     AsyncRedisStorage
)



@asynccontextmanager
async def create_storage(
     cls: type[BaseStorage],
     file_path: str,
) -> AsyncGenerator[BaseStorage, None]:
     instance = None
     shutdown = None
     
     async def file_remove() -> None:
          os.remove(file_path)
     
     async def redis_close() -> None:
          await instance.redis.aclose()
          
     async def memory_close() -> None:
          instance.storage.clear()
          
     if issubclass(cls, (FileStorage, FileLockStorage)):
          with open(file_path, "w"): ...
          instance = cls(file=file_path)
          shutdown = file_remove
          
     elif issubclass(cls, (AsyncRedisStorage, AsyncRedisLockStorage)):
          instance = cls(redis=Redis(protocol=2), expire=10)
          shutdown = redis_close
          
     else:
          instance = cls()
          shutdown = memory_close
          
     yield instance
     await shutdown()
     
     
          
@pytest.fixture(
     scope="function",
     params=[
          MemoryLockStorage,
          FileLockStorage, 
          AsyncRedisLockStorage
     ]
)
async def storage_lock(request) -> AsyncGenerator[BaseLockStorage, None]:
     async with create_storage(cls=request.param, file_path="./test_lock.txt") as storage:
          yield storage
          
          
@pytest.fixture(
     scope="function",
     params=[
          MemoryStorage,
          FileStorage, 
          AsyncRedisStorage
     ]
)
async def storage(request) -> AsyncGenerator[BaseStorage, None]:
     async with create_storage(cls=request.param, file_path="./test.txt") as storage:
          yield storage