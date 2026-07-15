# import pytest

# from typing import Optional
# from contextlib import nullcontext

# from redis.asyncio import Redis
# from aiogram import Dispatcher
# from aiogram_tool.tools.limit import setup_limit_tool
# from aiogram_tool.storage.base import StorageProtocol
# from aiogram_tool.storage import (
#      AsyncRedisStorage, 
#      MemoryStorage, 
#      MemoryLimitStorage, 
#      FileStorage
# )
# from aiogram_tool.utils.answer import (
#      CallbackDataAnswer, 
#      RateLimitAnswer
# )


# @pytest.mark.parametrize(
#      argnames=["storage", "context"],
#      argvalues=[
#           (None, pytest.raises(TypeError)),
#           (MemoryStorage(), nullcontext()),
#           (MemoryLimitStorage(memory_limit=10000), nullcontext()),
#           (FileStorage(file="test_file.txt"), nullcontext()),
#           (AsyncRedisStorage())
          
#      ]
# )
# def test_with_storages(
#      dispacher: Dispatcher, 
#      storage: Optional[StorageProtocol], 
#      context
# ) -> None:
#      with context:
#           setup_limit_tool(dispatcher=dispacher)

#           assert isinstance(dispacher["storage"], StorageProtocol)
#           assert dispacher["answer_callback"] is None
     
     
     

     


