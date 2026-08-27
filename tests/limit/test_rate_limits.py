import asyncio
import pytest
import secrets

from datetime import timedelta
from typing import Any, AsyncGenerator

from aiogram.types import Message
from aiogram.dispatcher.event.bases import UNHANDLED

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit import (
     RateLimitFilter,
     RateLimitAnswer,
     RateLimitTool
)
from aiogram_tool.tools.limit.rate_limit.base import BaseRateLimit
from aiogram_tool.tools.limit.rate_limit import (
     FixedWindowRateLimit,
     SlidingWindowRateLimit,
     TokenBucketRateLimit
)
from aiogram_tool.storage import (
     MemoryLockStorage,
     FileLockStorage,
     AsyncRedisLockStorage
)
from aiogram_tool.types import _MISSING

from .conftest import MyDispatcher
from ..conftest import create_storage



class MyAnswer(RateLimitAnswer):
     def __init__(self) -> None:
          self.is_pushed = False
          
     async def __call__(
          self, 
          event: Message, 
          window_time: timedelta, 
          retry_after: timedelta
     ) -> None:
          assert isinstance(event, Message)
          assert isinstance(window_time, timedelta)
          assert isinstance(retry_after, timedelta)
          self.is_pushed = True
          

@pytest.fixture(scope="function")
def my_answer() -> MyAnswer:
     return MyAnswer()

@pytest.fixture(scope="function")
def user_id() -> int:
     return secrets.randbits(30)

@pytest.fixture(
     scope="function",
     params=[
          MemoryLockStorage,
          FileLockStorage, 
          AsyncRedisLockStorage
     ]
)
async def local_storage_lock(request) -> AsyncGenerator[BaseLockStorage, None]:
     async with create_storage(cls=request.param, file_path="./local_test_lock.txt") as storage:
          yield storage


@pytest.mark.parametrize(
     argnames=("rate_limit", "results", "answer_result"),
     argvalues=(
          (
               FixedWindowRateLimit(
                    requests=2,
                    time=timedelta(seconds=1)
               ),
               [["handle", "handle"]],
               False
          ),
          (
               SlidingWindowRateLimit(
                    requests=2,
                    time=timedelta(seconds=1)
               ),
               [["handle", UNHANDLED], [UNHANDLED, "handle"]],
               True
          ),
          (
               TokenBucketRateLimit(
                    bucket_size=2,
                    current_tokens=2,
                    refill_time=timedelta(seconds=2),
                    refill_tokens=1
               ),
               [[UNHANDLED, UNHANDLED]],
               True
          )
     )
)  
async def test_with_setup(
     my_dispatcher: MyDispatcher,
     storage_lock: BaseLockStorage,
     my_answer: MyAnswer,
     rate_limit_tool: RateLimitTool,
     rate_limit: BaseRateLimit,
     user_id: int,
     results: list[list],
     answer_result: bool
) -> None:
     rate_limit_tool.storage = storage_lock
     rate_limit_tool.answer_callback = my_answer
     rate_limit_tool.setup(my_dispatcher)
     
     @my_dispatcher.message(
          RateLimitFilter(rate_limit=rate_limit)
     )
     async def handle(message: Message) -> str:
          assert isinstance(message, Message)
          return "handle"
     
     await my_dispatcher.message_update(user_id) == "handle"
     
     await asyncio.sleep(0.5)
     
     await my_dispatcher.message_update(user_id) == "handle"
     
     await asyncio.sleep(0.7)
     
     handle_results = await asyncio.gather(
          *[
               my_dispatcher.message_update(user_id=user_id),
               my_dispatcher.message_update(user_id=user_id),
          ]
     )
     assert handle_results in results
     assert my_answer.is_pushed is answer_result
     
     
@pytest.mark.parametrize(
     argnames=("rate_limit",),
     argvalues=(
          (
               FixedWindowRateLimit(
                    time=timedelta(seconds=1),
                    requests=1
               ),
          ),
          (
               SlidingWindowRateLimit(
                    time=timedelta(seconds=1),
                    requests=1
               ),
          ),
          (
               TokenBucketRateLimit(
                    bucket_size=1,
                    current_tokens=1
               ),
          )
     )
)
async def test_all_users(
     my_dispatcher: MyDispatcher,
     storage_lock: BaseLockStorage,
     my_answer: MyAnswer,
     rate_limit_tool: RateLimitTool,
     rate_limit: BaseRateLimit,
     user_id: int
) -> None:
     rate_limit_tool.storage = storage_lock
     rate_limit_tool.answer_callback = my_answer
     rate_limit_tool.setup(my_dispatcher)
     
     @my_dispatcher.message(
          RateLimitFilter(
               rate_limit=rate_limit,
               all_users=True
          )
     )
     async def handle(message: Message) -> str:
          assert isinstance(message, Message)
          return "handle"
     
     results = [
          await my_dispatcher.message_update(user_id=user_id),
          await my_dispatcher.message_update(user_id=secrets.randbits(30))
     ]
     assert results == ["handle", UNHANDLED]
     
     
@pytest.mark.parametrize(
     argnames=("rate_limit",),
     argvalues=(
          (
               FixedWindowRateLimit(
                    time=timedelta(seconds=1),
                    requests=1
               ),
          ),
          (
               SlidingWindowRateLimit(
                    time=timedelta(seconds=1),
                    requests=1
               ),
          ),
          (
               TokenBucketRateLimit(
                    bucket_size=1,
                    current_tokens=1
               ),
          )
     )
)
async def test_redifinition_and_key_in_filter(
     my_dispatcher: MyDispatcher,
     storage_lock: BaseLockStorage,
     local_storage_lock: BaseLockStorage,
     my_answer: MyAnswer,
     rate_limit_tool: RateLimitTool,
     rate_limit: BaseRateLimit,
     user_id: int
) -> None:
     rate_limit_tool.storage = storage_lock
     rate_limit_tool.answer_callback = my_answer
     rate_limit_tool.setup(my_dispatcher)
     
     class NewAnswer(RateLimitAnswer):
          def __init__(self) -> None:
               self.is_pushed = False
               
          async def __call__(
               self, 
               event: Message, 
               window_time: timedelta, 
               retry_after: timedelta
          ) -> None:
               assert isinstance(event, Message)
               assert isinstance(window_time, timedelta)
               assert isinstance(retry_after, timedelta)
               self.is_pushed = True
               
     new_answer = NewAnswer()
     
     @my_dispatcher.message(
          RateLimitFilter(
               rate_limit=rate_limit,
               answer_callback=new_answer,
               storage=local_storage_lock,
               key="redifinition"
          )
     )
     async def handle(message: Message) -> None:
          assert isinstance(message, Message)
          return "handle"
     
     results = [
          await my_dispatcher.message_update(user_id=user_id),
          await my_dispatcher.message_update(user_id=user_id)
     ]
     
     assert results == ["handle", UNHANDLED]
     assert new_answer.is_pushed is True
     assert my_answer.is_pushed is False
     
     key = f"{rate_limit.storage_prefix}@{user_id}@redifinition"
     local_value = await local_storage_lock.get_value(key)
     
     assert local_value is not _MISSING
     
     
     
@pytest.mark.parametrize(
     argnames=("rate_limit_class", "data"),
     argvalues=(
          (
               FixedWindowRateLimit,
               [
                    {"requests": 0, "time": timedelta(seconds=1)},
                    {"requests": -5, "time": timedelta(seconds=1)}
               ]
          ),
          (
               SlidingWindowRateLimit,
               [
                    {"requests": 0, "time": timedelta(seconds=1)},
                    {"requests": -5, "time": timedelta(seconds=1)}
               ]
          ),
          (
               TokenBucketRateLimit,
               [
                    {"bucket_size": 0},
                    {"bucket_size": -5},
                    {"current_tokens": 0, "bucket_size": 1},
                    {"current_tokens": -5, "bucket_size": 0},
                    {"refill_tokens": 0, "bucket_size": 0},
                    {"refill_tokens": -5, "bucket_size": 0}
               ]
          )
     )
)
async def test_limits_errors(
     rate_limit_class: BaseRateLimit,
     data: list[dict[str, Any]]
) -> None:
     for error_data in data:
          with pytest.raises(ValueError):
               rate_limit_class(**error_data)
     
