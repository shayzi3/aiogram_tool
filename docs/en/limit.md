# RateLimit — request rate limiting

A tool for limiting the rate of handler calls in [aiogram 3.x](https://github.com/aiogram/aiogram).

Supports three limiting algorithms — `FixedWindowRateLimit`, `SlidingWindowRateLimit` and `TokenBucketRateLimit`, — various storages (memory, file, Redis), per-user and global limits, custom keys and custom responses to the user when the limit is exceeded.

## How does it work?

Everything is built on two classes:

- `RateLimitTool` — registered **once** via `aiogram_tool_setup` and stores the **default** settings for all handlers: `storage` (limit storage) and `answer_callback` (response when the limit is exceeded). Upon registration, it saves itself to `dispatcher.workflow_data["rate_limit"]`.
- `RateLimitFilter` — a filter that is added to a **specific handler**. You can also pass `storage` and `answer_callback` to it — then they become attributes of this filter instance and will be used only by that handler.

When the filter is called, the following happens:

1. The filter finds `RateLimitTool` in `dispatcher.workflow_data` (if it is not there — `ValueError`).
2. `storage` and `answer_callback` are determined: if they were passed **directly to `RateLimitFilter`** — the filter's values are used (its own attributes). If `None` is passed to the filter (default) — the default values from `RateLimitTool` are taken.
3. A unique key of the form `{storage_prefix}@{user_id | "users"}@{key | module.qualname}` is built.
4. `rate_limit.execute(...)` is called under a lock (`storage.lock(key)`), so the limit check is atomic even with concurrent updates.

If the limit is not exhausted — the filter returns `True` and the handler is called. If it is exhausted — `answer_callback` is called, the filter returns `False`, and the handler is not called (aiogram will move on to the next handlers).

> [!CAUTION]
> Events without the `from_user` attribute are not supported — a `TypeError` will be raised.

> [!CAUTION]
> By default, the key is formed from the module name and the handler function (`module.qualname`). If two handlers have matching names — they will share a single limit. Use the `key` argument to set the key explicitly.

## Quick start

```python
import asyncio
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.limit import RateLimitTool, RateLimitFilter
from aiogram_tool.tools.limit.rate_limit import FixedWindowRateLimit


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


@dp.message(
    # Limit: 3 requests per 10 seconds per user
    Command("ping"),
    RateLimitFilter(
        rate_limit=FixedWindowRateLimit(requests=3, time=timedelta(seconds=10))
    ),
)
async def ping_handler(message: Message):
    await message.answer("Pong!")


async def main():
    # Initialization and registration of RateLimitTool
    # By default, MemoryLockStorage and RateLimitAnswer are used
    rate_limit_tool = RateLimitTool()
    aiogram_tool_setup(dp, [rate_limit_tool])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Limiting algorithms

### FixedWindowRateLimit — fixed window

A simple algorithm: the window opens with the first request and closes after `time`. Within the window, no more than `requests` requests are allowed, after which all requests are rejected until the end of the window. When the window expires, the counter is reset.

```python
RateLimitFilter(rate_limit=FixedWindowRateLimit(requests=5, time=timedelta(seconds=60)))
```

> [!TIP]
> "Bursts" are possible at the window boundary: a user can send `requests` requests at the end of one window and immediately `requests` more at the beginning of the next one. If this is critical — use `SlidingWindowRateLimit`.

### SlidingWindowRateLimit — sliding window

Stores timestamps of recent requests and takes into account only those that fall within the last `time`. The limit is no more than `requests` requests in any `time` period. More accurate than the fixed window and does not allow bursts at its boundary.

```python
RateLimitFilter(
    rate_limit=SlidingWindowRateLimit(requests=5, time=timedelta(seconds=60))
)
```

### TokenBucketRateLimit — token bucket

The classic token bucket algorithm: tokens accumulate in the "bucket" (no more than `bucket_size`), and each request consumes one token. Tokens are refilled at a rate of `refill_tokens` every `refill_time`. It allows short-term bursts (thanks to accumulated tokens) and smoothly limits the average request rate.

```python
RateLimitFilter(
    rate_limit=TokenBucketRateLimit(
        bucket_size=5,  # maximum number of tokens
        current_tokens=5,  # initial number of tokens
        refill_time=timedelta(seconds=5),  # refill interval
        refill_tokens=1,  # +1 token every 5 seconds
    )
)
```

### Algorithm comparison

| Algorithm | Arguments | Features |
|---|---|---|
| `FixedWindowRateLimit` | `requests`, `time` | Simple, minimal data in storage; bursts possible at the window boundary |
| `SlidingWindowRateLimit` | `requests`, `time` | Accurate, no bursts; stores a list of timestamps |
| `TokenBucketRateLimit` | `bucket_size`, `current_tokens`, `refill_time`, `refill_tokens` | Bursts allowed, average rate limited by the refill rate |

## Per-user and global limits

By default, the limit applies **to each user separately** (`user_id` is included in the key). With the `all_users=True` argument, the limit becomes **shared for all users**:

```python
@dp.message(
    Command("start"),
    RateLimitFilter(
        rate_limit=SlidingWindowRateLimit(requests=10, time=timedelta(minutes=1)),
        all_users=True,  # the limit is shared for everyone
        key="global_start",  # custom key instead of the handler name
    ),
)
async def start_handler(message: Message):
    await message.answer("10 requests per minute for everyone")
```

## Custom response when the limit is exceeded

The default response (`RateLimitAnswer`) sends text like `Next request after 7.0 seconds.`. To change it — inherit from `RateLimitAnswer` and override `__call__`:

```python
from datetime import timedelta

from aiogram.types import TelegramObject

from aiogram_tool.tools.limit import RateLimitAnswer


class CustomLimitAnswer(RateLimitAnswer):
    async def __call__(
        self, event: TelegramObject, window_time: timedelta, retry_after: timedelta
    ) -> None:
        await event.answer(
            text=f"🚫 Too many requests! Try again in {retry_after.total_seconds():.1f} sec."
        )


rate_limit_tool = RateLimitTool(
    answer_callback=CustomLimitAnswer()  # default for all handlers
)
```

`__call__` arguments:

- `event` — the Telegram event (`TelegramObject`);
- `window_time` — the window set at the handler level (for `TokenBucketRateLimit` — the time to refill one token);
- `retry_after` — the time until the next allowed request.

> [!TIP]
> `answer_callback` can also be passed directly to the `RateLimitFilter` of a specific handler — then it will be used instead of the value from `RateLimitTool`.

## Overriding storage and answer_callback in the filter

`storage` and `answer_callback` can be passed directly to a `RateLimitFilter` instance — in this case, they become attributes of that specific filter and apply only to its handler, without affecting the others:

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.storage import AsyncRedisLockStorage


@dp.message(
    Command("secret"),
    RateLimitFilter(
        rate_limit=SlidingWindowRateLimit(requests=2, time=timedelta(seconds=30)),
        storage=AsyncRedisLockStorage(redis=AsyncRedis()),  # own storage
        answer_callback=RateLimitAnswer(),  # own response
        key="secret_cmd",  # own key
    ),
)
async def secret_handler(message: Message):
    await message.answer("Limit: 2 requests per 30 seconds.")
```

## Storages

Limits are stored in `BaseLockStorage` — a storage with lock support:

| Storage | Description |
|---|---|
| `MemoryLockStorage` | **Default.** Data in the process memory; reset on restart |
| `FileLockStorage` | Data in a file (`file=path`); survive a restart |
| `AsyncRedisLockStorage` | Data in Redis (`redis=AsyncRedis(...)`); suitable for multiple bot instances |

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.storage import AsyncRedisLockStorage


rate_limit_tool = RateLimitTool(storage=AsyncRedisLockStorage(redis=AsyncRedis()))
aiogram_tool_setup(dp, [rate_limit_tool])
```

> [!TIP]
> For horizontal scaling (multiple bot instances), use `AsyncRedisLockStorage` — locks and counters will be shared.

## API reference

`function: aiogram_tool_setup`

    arguments:
        dispatcher: Dispatcher - (required)
        tools: Iterable[BaseTool] - (required)

    The main function for registering tools. For rate limiting, pass
    a RateLimitTool class instance in the tools list.


`class: RateLimitTool`

    arguments:
        storage: BaseLockStorage - (default MemoryLockStorage())
        answer_callback: RateLimitAnswer - (default RateLimitAnswer())

    Stores the default settings (storage and answer_callback) for all
    handlers. When setup is called, it saves itself to
    dispatcher.workflow_data["rate_limit"], from where filters get it.

    Argument documentation:

    1. storage — the default limit storage for all handlers.

    2. answer_callback — the default response when the limit is
    exceeded for all handlers.


`class: RateLimitFilter`

    arguments:
        rate_limit: BaseRateLimit - (required)
        storage: BaseLockStorage - (default None)
        answer_callback: RateLimitAnswer - (default None)
        key: str - (default None)
        all_users: bool - (default False)

    Handler call rate limiting filter. Returns True if the request
    is allowed, and False if the limit is exhausted (answer_callback
    is called before that).

    Argument documentation:

    1. rate_limit — the limiting algorithm: FixedWindowRateLimit,
    SlidingWindowRateLimit, TokenBucketRateLimit or your own class
    based on BaseRateLimit.

    2. storage — the storage for this handler. Values passed to the
    filter become its attributes and take priority over the values
    from RateLimitTool. If None — the storage from RateLimitTool is used.

    3. answer_callback — the response for this handler. Similar to
    storage: the filter argument takes priority over RateLimitTool.
    If None — the answer_callback from RateLimitTool is used.

    4. key — the key for identifying the limit. By default,
    "module.handler_name" (module.qualname) is used.

    5. all_users — if True, the limit is shared for all users,
    not per-user.


`class: RateLimitAnswer`

    arguments (__call__ method):
        event: TelegramObject - (required)
        window_time: timedelta - (required)
        retry_after: timedelta - (required)

    The default response when the limit is exceeded: sends the text
    "Next request after {retry_after} seconds.".

    For a custom response, inherit from the class and override
    async __call__.


`class: BaseRateLimit`

    The base abstract class of limiting algorithms.

    Attributes:
        storage_prefix: str - the key prefix in the storage
        ("fixed_aiot_rate_limit", "sliding_aiot_rate_limit",
        "token_bucket_aiot_rate_limit")

    Methods:
        build_key(event, unique_handler_name, all_users, key) - builds a key
        of the form "{storage_prefix}@{user_id | "users"}@{key | handler_name}"
        execute(event, storage, answer_callback, key) - abstract method:
        checks the limit and returns bool

    For your own algorithm, inherit from BaseRateLimit
    and implement execute.


`class: FixedWindowRateLimit`

    arguments:
        requests: int - (required)
        time: timedelta - (required)

    Fixed window: no more than requests requests per time.
    requests <= 0 — ValueError.


`class: SlidingWindowRateLimit`

    arguments:
        requests: int - (required)
        time: timedelta - (required)

    Sliding window: no more than requests requests in any time period.
    requests <= 0 — ValueError.


`class: TokenBucketRateLimit`

    arguments:
        bucket_size: int - (required)
        current_tokens: int - (default 1)
        refill_time: timedelta - (default timedelta(seconds=1))
        refill_tokens: int - (default 1)

    Token bucket: bucket_size — the maximum number of tokens,
    current_tokens — the initial number of tokens, refill_tokens
    are refilled every refill_time.
    bucket_size, current_tokens, refill_tokens <= 0 — ValueError.


`class: UserLimit`

    arguments:
        requests: int | float - (required)
        time: datetime - (required)

    A data class for storing the limit state in the storage (serialized
    to JSON). Used by the FixedWindow and TokenBucket algorithms.


## Exceptions

| Exception | When it is raised |
|---|---|
| `ValueError` | Invalid algorithm arguments: `requests <= 0` (Fixed/Sliding Window), `bucket_size`/`current_tokens`/`refill_tokens <= 0` (Token Bucket) |
| `ValueError("Dispatcher not found")` | The dispatcher was not found in the update data (see the note below) |
| `ValueError("Not found RateLimitTool. Call setup function")` | `RateLimitFilter` is used without a registered `RateLimitTool` |
| `TypeError` | The event does not have the `from_user` attribute |


> [!CAUTION]
> The filter gets `RateLimitTool` through the dispatcher, which is searched for in the update data. With standard polling, this works automatically. If you process updates manually (for example, a webhook via `feed_update`), pass the keyword argument `dispatcher=instance of the Dispatcher class`, otherwise the filter will raise `ValueError("Dispatcher not found")`.


[All code examples can be found here](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/)