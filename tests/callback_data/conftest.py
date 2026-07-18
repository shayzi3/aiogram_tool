import pytest
import secrets
import os

from typing import AsyncGenerator, Callable

from redis.asyncio import Redis
from aiogram.types import CallbackQuery, User

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.storage import MemoryStorage, FileStorage, AsyncRedisStorage


CallbackQueryFactoryType = Callable[[str | None], CallbackQuery]


@pytest.fixture(
     scope="function",
     params=[MemoryStorage, FileStorage, AsyncRedisStorage]
)
async def storage(request) -> AsyncGenerator[BaseStorage, None]:
     instance = None
     param = request.param
     
     if param is FileStorage:
          with open("./test.txt", "w"): ...
          instance = param(file="./test.txt")
          
     elif param is AsyncRedisStorage:
          instance = param(redis=Redis(protocol=2), expire=60)
     
     else:
          instance = param()
     
     yield instance
     
     if isinstance(instance, FileStorage):
          os.remove("./test.txt")
     
     elif isinstance(instance, AsyncRedisStorage):
          await instance.redis.aclose()
          

@pytest.fixture(scope="session")
def callback_query_factory() -> CallbackQueryFactoryType:
     def factory(callback_data: str | None) -> CallbackQuery:
          return CallbackQuery(
               id=str(secrets.randbits(k=10)),
               chat_instance="instance",
               data=callback_data,
               from_user=User(
                    id=secrets.randbits(k=10),
                    is_bot=False,
                    first_name="Vlad"
               )
          )
     return factory
          
     