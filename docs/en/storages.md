# Storages

The `aiogram_tool.storage` module provides backends for storing tool state (rate limiting, long callback data, etc.) and locks.

- **Package:** `aiogram_tool/storage/`
- **Public imports:** `aiogram_tool.storage` re-exports all classes (`FileStorage`, `FileLockStorage`, `MemoryStorage`, `MemoryLockStorage`, `AsyncRedisStorage`, `AsyncRedisLockStorage`)

## Overview

| Storage | Inheritance | Persistence | Locks |
|---|---|---|---|
| `MemoryStorage` | `BaseStorage` | In memory (lost on restart) | ❌ |
| `MemoryLockStorage` | `MemoryStorage`, `BaseLockStorage` | In memory | ✅ |
| `AsyncRedisStorage` | `BaseStorage` | Redis (survives restart, shared across instances) | ❌ |
| `AsyncRedisLockStorage` | `AsyncRedisStorage`, `BaseLockStorage` | Redis | ✅ |
| `FileStorage` | `MemoryStorage` | Local file | ❌ |
| `FileLockStorage` | `FileStorage`, `BaseLockStorage` | Local file + memory | ✅ |

## Interfaces

### `BaseStorage` (`aiogram_tool.storage.base`)

```python
class BaseStorage(ABC):
    async def set_value(self, key: str, value: str) -> None: ...
    async def get_value(self, key: str) -> str | _MISSING: ...
```

- `get_value` returns a `str` or the `_MISSING` sentinel (`aiogram_tool.types._MISSING`) if the key is absent. Do not use `None` as an absence check.

### `BaseLockStorage`

```python
class BaseLockStorage(BaseStorage):
    async def lock(self, key: str) -> AbstractAsyncContextManager[None]: ...
```

The `lock(key)` method returns an async context manager that locks by key:

```python
async with storage.lock("my_key"):
    ...  # critical section
```

---

## MemoryStorage

The simplest storage based on `dict` (or rather, any `MutableMapping`). Suitable for development, tests, and bots without persistence requirements.

```python
MemoryStorage(storage: MutableMapping | None = None)
```

- `storage` — an optional external mapping (useful for tests and pre-filling).

> As a `MutableMapping` you can pass not only a `dict`, but also caches from [`cachetools`](https://github.com/uri-grants/cachetools) — for example, `Cache` or `TTLCache` (with automatic eviction by size or TTL).

```python
from aiogram_tool.storage import MemoryStorage

storage = MemoryStorage()
await storage.set_value("key", "value")
value = await storage.get_value("key")  # "value"
```

## MemoryLockStorage

Same as `MemoryStorage`, plus locks based on `asyncio.Lock`. `lock(key)` lazily creates and returns an `asyncio.Lock` for the key, protected by a global internal lock.

```python
MemoryLockStorage(
    storage: MutableMapping | None = None,
    locks_storage: MutableMapping | None = None,
)
```

- `locks_storage` — an external mapping for the locks themselves (optional).

⚠️ Locks only work within the current process — not suitable for multiple bot instances.

```python
from aiogram_tool.storage import MemoryLockStorage

storage = MemoryLockStorage()
async with storage.lock("user:123"):
    ...
```

## AsyncRedisStorage

A Redis-backed storage (`redis.asyncio.Redis`). Recommended for production: state survives restarts and is shared between instances.

```python
AsyncRedisStorage(redis: AsyncRedis, expire: int | None = None)
```

- `redis` — a `redis.asyncio.Redis` client
- `expire` — TTL in seconds for each entry; `None` — no expiration

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisStorage

storage = AsyncRedisStorage(redis=AsyncRedis(), expire=3600)
await storage.set_value("key", "value")
value = await storage.get_value("key")  # "value" (bytes are decoded automatically)
```

The value passed to `set_value` does not have to be a `str` — it is passed to Redis as is.

## AsyncRedisLockStorage

A Redis storage with distributed locks (`redis.asyncio.lock.Lock`).

```python
AsyncRedisLockStorage(redis: AsyncRedis, expire: int | None = None)
```

`lock(key)` returns a Redis lock with the key `aigram_tool_lock:{key}`, `timeout=10` and `blocking_timeout=10` (seconds). Suitable for multiple bot instances.

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisLockStorage

storage = AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)
async with storage.lock("my_key"):
    ...
```

## FileStorage

A storage in a text file (format: `key&value` lines). Inherits from `MemoryStorage`.

```python
FileStorage(file: str, storage: MutableMapping | None = None)
```

- `file` — path to an existing file; if the file is missing, `FileNotFoundError` is raised
- `storage` — an optional internal `MutableMapping` cache; if provided, the "file + memory" mode is enabled: reads check the cache first and cache results read from the file

Features:

- The `&` symbol is forbidden in keys (`ValueError`)
- Entries are appended to the end of the file (`a`); reads go from the end of the file — the last write for a key wins
- Values may contain `&` (parsing uses `maxsplit=1`)

```python
from aiogram_tool.storage import FileStorage

storage = FileStorage(file="state.txt", storage={})
await storage.set_value("key", "value")
value = await storage.get_value("key")
```

> The file must exist before the storage is created — create it in advance if necessary (e.g. `Path("state.txt").touch()`).

## FileLockStorage

`FileStorage` + locks based on `asyncio.Lock` (same as `MemoryLockStorage`).

```python
FileLockStorage(
    file: str,
    storage: MutableMapping | None = None,
    locks_storage: MutableMapping | None = None,
)
```

Data is persisted in the file, but locks are process-local.

## Passing storages to tools

Storages are usually passed to a tool's constructor when calling `aiogram_tool_setup`:

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.limit import RateLimitTool
from aiogram_tool.storage import AsyncRedisLockStorage

aiogram_tool_setup(
    dp,
    [
        RateLimitTool(storage=AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)),
    ],
)
```

A callback data example:

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.tools.callback_data import LongCallbackData
from aiogram_tool.storage import AsyncRedisLockStorage


class PersistentData(LongCallbackData, prefix="redis"):
    _storage = AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)
    user_id: int
    big_context: str
```

## Choosing a storage

- **Development / tests** → `MemoryStorage` / `MemoryLockStorage`
- **Production, single instance, no Redis** → `FileStorage` / `FileLockStorage`
- **Production, multiple instances, or reliability needed** → `AsyncRedisStorage` / `AsyncRedisLockStorage`

## Limitations

- Locks of `MemoryLockStorage` and `FileLockStorage` do not work across processes — use `AsyncRedisLockStorage` for multiple workers
- `FileStorage` performs a full scan of the file on every read (without a cache) — use Redis for large volumes of data
- `FileStorage` requires an existing file and forbids `&` in keys
