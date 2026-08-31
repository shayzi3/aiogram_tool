# aiogram_tool

A collection of powerful tools and utilities for [aiogram 3.x](https://github.com/aiogram/aiogram) — dependency injection, rate limiting, and long callback data support.

## ✨ Features

- **Dependency Injection** — inject dependencies into handlers with `Depends()`, similar to FastAPI. Supports classes, functions, scopes (`SINGLETON`, `REQUEST`, `TRANSIENT`), nested dependencies, and more.
- **Rate Limiter** — limit how often handlers can be called. Three built-in algorithms: Fixed Window, Sliding Window, and Token Bucket. Works per-user or globally.
- **Long Callback Data** — bypass Telegram's 64-byte `callback_data` limit. Pack large payloads into inline keyboard buttons transparently.
- **Pluggable Storage** — Memory, Redis, and File storage backends for persisting rate-limit and callback data state.

## 📦 Installation

Requires **Python 3.11+** and **aiogram 3.x**.

### pip

```bash
pip install aiogram_tool
```

### Poetry

```bash
poetry add aiogram_tool
```

### uv

```bash
uv add aiogram_tool
```

## 🚀 Quick Start

Register tools on your dispatcher with `aiogram_tool_setup`:

```python
from aiogram import Bot, Dispatcher
from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.depend import DependTool
from aiogram_tool.tools.limit import RateLimitTool

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()

aiogram_tool_setup(dp, [DependTool(), RateLimitTool()])

await dp.start_polling(bot)
```

## 🧰 Tools

### Dependency Injection

Inject dependencies into handlers via default argument values — no middleware boilerplate required.

```python
from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.depend import Depends, DependTool, ScopeRegistry, Scope

scope_registry = ScopeRegistry()


class CounterService:
    def __init__(self) -> None:
        self.count = 0

    async def __call__(self, context) -> dict:
        self.count += 1
        return {"current_count": self.count}


counter = CounterService()
scope_registry.register(counter, Scope.REQUEST)

# Pass the registry to the tool during setup
aiogram_tool_setup(dp, [DependTool(scope_registry=scope_registry)])


@dp.message(CommandStart())
async def start_handler(message: Message, stats: dict = Depends(counter)):
    await message.answer(f"Pressed: {stats['current_count']} times")
```

Highlights:

- Works with functions, class-functors, and `__init__` methods
- Scopes: `SINGLETON`, `REQUEST`, `TRANSIENT` (via `ScopeRegistry`)
- Nested dependencies (`subdepends`), `From` extractor, `DependFilter`, and `DependExit`

📖 Full documentation: [EN](docs/en/depend.md) | [RU](docs/ru/depend.md)

### Rate Limiter

Limit handler calls with three built-in algorithms:

```python
from datetime import timedelta
from aiogram_tool.tools.limit import RateLimitTool, RateLimitFilter
from aiogram_tool.tools.limit.rate_limit import SlidingWindowRateLimit


@dp.message(
    Command("ping"),
    # 3 requests per 10 seconds per user
    RateLimitFilter(
        rate_limit=SlidingWindowRateLimit(
            requests=3,
            time=timedelta(seconds=10),
        )
    ),
)
async def ping_handler(message: Message):
    await message.answer("Pong!")
```

Available algorithms:

| Algorithm | Description |
|---|---|
| `FixedWindowRateLimit` | N requests per fixed time window |
| `SlidingWindowRateLimit` | More accurate; prevents bursts at window edges |
| `TokenBucketRateLimit` | Bucket of tokens that refills over time |

Extras:

- `all_users=True` — apply the limit globally instead of per-user
- `key="..."` — custom rate-limit key
- Custom `RateLimitAnswer` — control the response when the limit is exceeded
- Redis storage — share limits across bot restarts and multiple instances

📖 Full documentation: [EN](docs/en/limit.md) | [RU](docs/ru/limit.md)

### Long Callback Data

Telegram limits `callback_data` to **64 bytes**. `LongCallbackData` automatically stores oversized payloads and restores them when the callback arrives — with the same familiar aiogram API.

```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram_tool.tools.callback_data import LongCallbackData

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


class MyData(LongCallbackData, prefix="mydata"):
    mode: str
    payload: str


@dp.message(CommandStart())
async def start_handler(message: Message):
    # Short data is packed as usual; long data is stored transparently
    short_cb = await MyData(mode="short", payload="Hello!").pack_long()
    long_cb = await MyData(mode="long", payload="A" * 200).pack_long()

    await message.answer(
        "Choose an action:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Short data", callback_data=short_cb)],
                [InlineKeyboardButton(text="Long data", callback_data=long_cb)],
            ]
        ),
    )


# Filter exactly like standard aiogram CallbackData
@dp.callback_query(MyData.filter(F.mode == "long"))
async def handler(query: CallbackQuery, callback_data: MyData):
    # Original data is fully available despite the 64-byte limit
    await query.answer(text=f"Received: {callback_data.payload}")
```

By default data is kept in in-memory storage. Use Redis to persist it across restarts:

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisLockStorage


class PersistentData(LongCallbackData, prefix="redis"):
    _storage = AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)
    user_id: int
    big_context: str
```

📖 Full documentation: [EN](docs/en/callback_data.md) | [RU](docs/ru/callback_data.md)

## 💾 Storage Backends

| Storage | Persistence | Lock support |
|---|---|---|
| `MemoryStorage` / `MemoryLockStorage` | In-memory | ✅ |
| `AsyncRedisStorage` / `AsyncRedisLockStorage` | Redis (survives restarts) | ✅ |
| `FileStorage` / `FileLockStorage` | Local files | ✅ |

## 📁 Examples

Ready-to-run examples are available in the [`examples/`](examples/) directory:

- [Dependency Injection](examples/depend/) — classes, scopes, overrides, sub-dependencies
- [Rate Limiting](examples/limit/) — basic usage, algorithms, advanced configuration
- [Callback Data](examples/callback_data/) — basic usage, custom answers, Redis storage

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the terms of the [LICENSE.md](LICENSE.md).