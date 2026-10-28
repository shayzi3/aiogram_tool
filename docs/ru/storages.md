# Хранилища (storage)

## Обзор

| Хранилище | Наследование | Персистентность | Блокировки |
|---|---|---|---|
| `MemoryStorage` | `BaseStorage` | В памяти (теряется при перезапуске) | ❌ |
| `MemoryLockStorage` | `MemoryStorage`, `BaseLockStorage` | В памяти | ✅ |
| `AsyncRedisStorage` | `BaseStorage` | Redis (переживает перезапуск, общий для инстансов) | ❌ |
| `AsyncRedisLockStorage` | `AsyncRedisStorage`, `BaseLockStorage` | Redis | ✅ |
| `FileStorage` | `MemoryStorage` | Локальный файл | ❌ |
| `FileLockStorage` | `FileStorage`, `BaseLockStorage` | Локальный файл + память | ✅ |

## Интерфейсы

### `BaseStorage` (`aiogram_tool.storage.base`)

```python
class BaseStorage(ABC):
    async def set_value(self, key: str, value: str) -> None: ...
    async def get_value(self, key: str) -> str | _MISSING: ...
```

- `get_value` возвращает `str` или sentinel `_MISSING` (`aiogram_tool.types._MISSING`), если ключа нет. Не используйте `None` как проверку отсутствия.

### `BaseLockStorage`

```python
class BaseLockStorage(BaseStorage):
    async def lock(self, key: str) -> AbstractAsyncContextManager[None]: ...
```

Метод `lock(key)` возвращает асинхронный контекстный менеджер блокировки по ключу:

```python
async with storage.lock("my_key"):
    ...  # критическая секция
```

---

## MemoryStorage

Простейшее хранилище на базе `dict` (точнее — любого `MutableMapping`). Подходит для разработки, тестов и ботов без требований к персистентности.

```python
MemoryStorage(storage: MutableMapping | None = None)
```

- `storage` — опциональный внешний словарь (полезно для тестов и предзаполнения).

> В качестве `MutableMapping` можно передавать не только `dict`, но и кэши из [`cachetools`](https://github.com/uri-grants/cachetools) — например, `Cache` или `TTLCache` (с автоматическим вытеснением по размеру или TTL).

```python
from aiogram_tool.storage import MemoryStorage

storage = MemoryStorage()
await storage.set_value("key", "value")
value = await storage.get_value("key")  # "value"
```

## MemoryLockStorage

То же, что `MemoryStorage`, плюс блокировки на `asyncio.Lock`. `lock(key)` лениво создаёт и возвращает `asyncio.Lock` для ключа под защитой глобального внутреннего лока.

```python
MemoryLockStorage(
    storage: MutableMapping | None = None,
    locks_storage: MutableMapping | None = None,
)
```

- `locks_storage` — внешний словарь для самих локов (опционально).

⚠️ Блокировки действуют только внутри текущего процесса — не подходят для нескольких инстансов бота.

```python
from aiogram_tool.storage import MemoryLockStorage

storage = MemoryLockStorage()
async with storage.lock("user:123"):
    ...
```
## AsyncRedisStorage

Хранилище на Redis (`redis.asyncio.Redis`). Рекомендуется для продакшена: состояние переживает перезапуск и разделяется между инстансами.

```python
AsyncRedisStorage(redis: AsyncRedis, expire: int | None = None)
```

- `redis` — клиент `redis.asyncio.Redis`
- `expire` — TTL в секундах для каждой записи; `None` — без истечения

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisStorage

storage = AsyncRedisStorage(redis=AsyncRedis(), expire=3600)
await storage.set_value("key", "value")
value = await storage.get_value("key")  # "value" (bytes автоматически декодируются)
```

Значение, передаваемое в `set_value`, не обязано быть `str` — оно передаётся в Redis как есть.

## AsyncRedisLockStorage

Redis-хранилище с распределёнными блокировками (`redis.asyncio.lock.Lock`).

```python
AsyncRedisLockStorage(redis: AsyncRedis, expire: int | None = None)
```

`lock(key)` возвращает Redis-лок с ключом `aigram_tool_lock:{key}`, `timeout=10` и `blocking_timeout=10` (секунды). Подходит для нескольких инстансов бота.

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisLockStorage

storage = AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)
async with storage.lock("my_key"):
    ...
```

## FileStorage

Хранилище в текстовом файле (формат: строки `key&value`). Наследуется от `MemoryStorage`.

```python
FileStorage(file: str, storage: MutableMapping | None = None)
```

- `file` — путь к существующему файлу; если файла нет, выбрасывается `FileNotFoundError`
- `storage` — опциональный внутренний `MutableMapping`-кэш; если передан, включается режим «file + memory»: чтение сначала проверяет кэш и кэширует результаты чтения из файла

Особенности:

- Символ `&` запрещён в ключах (`ValueError`)
- Записи добавляются в конец файла (`a`); чтение идёт с конца файла — выигрывает последняя запись по ключу
- Значения могут содержать `&` (парсинг использует `maxsplit=1`)

```python
from aiogram_tool.storage import FileStorage

storage = FileStorage(file="state.txt", storage={})
await storage.set_value("key", "value")
value = await storage.get_value("key")
```

> Файл должен существовать до создания хранилища — при необходимости создайте его заранее (например, `Path("state.txt").touch()`).

## FileLockStorage

`FileStorage` + блокировки на `asyncio.Lock` (как у `MemoryLockStorage`).

```python
FileLockStorage(
    file: str,
    storage: MutableMapping | None = None,
    locks_storage: MutableMapping | None = None,
)
```

Данные персистентны в файле, но блокировки локальны для процесса.

## Как передавать хранилища в инструменты

Хранилища обычно передаются конструктору инструмента при вызове `aiogram_tool_setup`:

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

Пример с callback data:

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.tools.callback_data import LongCallbackData
from aiogram_tool.storage import AsyncRedisLockStorage


class PersistentData(LongCallbackData, prefix="redis"):
    _storage = AsyncRedisLockStorage(redis=AsyncRedis(), expire=3600)
    user_id: int
    big_context: str
```

## Выбор хранилища

- **Разработка / тесты** → `MemoryStorage` / `MemoryLockStorage`
- **Продакшен, один инстанс, без Redis** → `FileStorage` / `FileLockStorage`
- **Продакшен, несколько инстансов или нужна надёжность** → `AsyncRedisStorage` / `AsyncRedisLockStorage`

## Ограничения

- Локи `MemoryLockStorage` и `FileLockStorage` не работают между процессами — для нескольких воркеров используйте `AsyncRedisLockStorage`
- `FileStorage` выполняет полный проход по файлу при каждом чтении (без кэша) — для больших объёмов данных используйте Redis
- `FileStorage` требует существования файла и запрещает `&` в ключах
