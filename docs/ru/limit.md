# RateLimit — ограничение частоты запросов (rate limiting)

Инструмент для ограничения частоты вызова обработчиков [aiogram 3.x](https://github.com/aiogram/aiogram).

Поддерживает три алгоритма ограничения — `FixedWindowRateLimit`, `SlidingWindowRateLimit` и `TokenBucketRateLimit`, — различные хранилища (память, файл, Redis), персональные и глобальные лимиты, кастомные ключи и собственные ответы пользователю при превышении лимита.

## Как это работает?

Всё построено на двух классах:

- `RateLimitTool` — регистрируется **один раз** через `aiogram_tool_setup` и хранит настройки **по умолчанию** для всех обработчиков: `storage` (хранилище лимитов) и `answer_callback` (ответ при превышении лимита). При регистрации он сохраняет себя в `dispatcher.workflow_data["rate_limit"]`.
- `RateLimitFilter` — фильтр, который добавляется в **конкретный обработчик**. В него также можно передать `storage` и `answer_callback` — тогда они станут атрибутами этого экземпляра фильтра и будут использоваться только этим обработчиком.

При вызове фильтра происходит следующее:

1. Фильтр находит `RateLimitTool` в `dispatcher.workflow_data` (если его там нет — `ValueError`).
2. Определяются `storage` и `answer_callback`: если они были переданы **напрямую в `RateLimitFilter`** — используются значения фильтра (его собственные атрибуты). Если в фильтр передано `None` (по умолчанию) — берутся значения по умолчанию из `RateLimitTool`.
3. Строится уникальный ключ вида `{storage_prefix}@{user_id | "users"}@{key | module.qualname}`.
4. Вызывается `rate_limit.execute(...)` под блокировкой (`storage.lock(key)`), благодаря чему проверка лимита атомарна даже при конкурентных апдейтах.

Если лимит не исчерпан — фильтр возвращает `True` и обработчик вызывается. Если исчерпан — вызывается `answer_callback`, фильтр возвращает `False`, и обработчик не вызывается (aiogram перейдёт к следующим обработчикам).

> [!CAUTION]
> События без атрибута `from_user` не поддерживаются — будет выброшено `TypeError`.

> [!CAUTION]
> По умолчанию ключ формируется из имени модуля и функции обработчика (`module.qualname`). Если у двух обработчиков совпадут имена — они будут делить один лимит. Используйте аргумент `key`, чтобы задать ключ явно.

## Быстрый старт

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
    # Лимит: 3 запроса в 10 секунд на пользователя
    Command("ping"),
    RateLimitFilter(
        rate_limit=FixedWindowRateLimit(
            requests=3,
            time=timedelta(seconds=10)
        )
    ),
)
async def ping_handler(message: Message):
    await message.answer("Pong!")


async def main():
    # Инициализация и регистрация RateLimitTool
    # По умолчанию используются MemoryLockStorage и RateLimitAnswer
    rate_limit_tool = RateLimitTool()
    aiogram_tool_setup(dp, [rate_limit_tool])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Алгоритмы ограничения

### FixedWindowRateLimit — фиксированное окно

Простой алгоритм: окно открывается с первого запроса и закрывается через `time`. Внутри окна разрешено не более `requests` запросов, после чего до конца окна все запросы отклоняются. По истечении окна счётчик сбрасывается.

```python
RateLimitFilter(
    rate_limit=FixedWindowRateLimit(
        requests=5,
        time=timedelta(seconds=60)
    )
)
```

> [!TIP]
> Возможны «всплески» на границе окна: пользователь может отправить `requests` запросов в конце одного окна и сразу `requests` в начале следующего. Если это критично — используйте `SlidingWindowRateLimit`.

### SlidingWindowRateLimit — скользящее окно

Хранит timestamps последних запросов и учитывает только те, что попадают в последние `time`. Лимит — не более `requests` запросов за любые `time`. Точнее фиксированного окна и не допускает всплесков на его границе.

```python
RateLimitFilter(
    rate_limit=SlidingWindowRateLimit(
        requests=5,
        time=timedelta(seconds=60)
    )
)
```

### TokenBucketRateLimit — токеновое ведро

Классический алгоритм token bucket: в «ведре» накапливаются токены (не больше `bucket_size`), каждый запрос расходует один токен. Токены пополняются со скоростью `refill_tokens` каждые `refill_time`. Позволяет кратковременные всплески (за счёт накопленных токенов) и плавно ограничивает среднюю частоту запросов.

```python
RateLimitFilter(
    rate_limit=TokenBucketRateLimit(
        bucket_size=5,                     # максимальное число токенов
        current_tokens=5,                  # начальное число токенов
        refill_time=timedelta(seconds=5),  # интервал пополнения
        refill_tokens=1                    # +1 токен каждые 5 секунд
    )
)
```

### Сравнение алгоритмов

| Алгоритм | Аргументы | Особенности |
|---|---|---|
| `FixedWindowRateLimit` | `requests`, `time` | Простой, минимум данных в хранилище; возможны всплески на границе окна |
| `SlidingWindowRateLimit` | `requests`, `time` | Точный, без всплесков; хранит список timestamps |
| `TokenBucketRateLimit` | `bucket_size`, `current_tokens`, `refill_time`, `refill_tokens` | Всплески разрешены, средняя частота ограничена скоростью пополнения |

## Персональные и глобальные лимиты

По умолчанию лимит действует **на каждого пользователя отдельно** (в ключ входит `user_id`). С аргументом `all_users=True` лимит становится **общим для всех пользователей**:

```python
@dp.message(
    Command("start"),
    RateLimitFilter(
        rate_limit=SlidingWindowRateLimit(
            requests=10,
            time=timedelta(minutes=1)
        ),
        all_users=True,     # лимит общий для всех
        key="global_start"  # свой ключ вместо имени обработчика
    ),
)
async def start_handler(message: Message):
    await message.answer("10 запросов в минуту на всех")
```

## Кастомный ответ при превышении лимита

Ответ по умолчанию (`RateLimitAnswer`) отправляет текст вида `Next request after 7.0 seconds.`. Чтобы изменить его — унаследуйтесь от `RateLimitAnswer` и переопределите `__call__`:

```python
from datetime import timedelta

from aiogram.types import TelegramObject

from aiogram_tool.tools.limit import RateLimitAnswer


class CustomLimitAnswer(RateLimitAnswer):
    async def __call__(
        self,
        event: TelegramObject,
        window_time: timedelta,
        retry_after: timedelta
    ) -> None:
        await event.answer(
            text=f"🚫 Слишком часто! Повторите через {retry_after.total_seconds():.1f} сек."
        )


rate_limit_tool = RateLimitTool(
    answer_callback=CustomLimitAnswer()  # по умолчанию для всех обработчиков
)
```

Аргументы `__call__`:

- `event` — событие Telegram (`TelegramObject`);
- `window_time` — окно, заданное на уровне обработчика (для `TokenBucketRateLimit` — время пополнения одного токена);
- `retry_after` — время до следующего разрешённого запроса.

> [!TIP]
> `answer_callback` можно передать и напрямую в `RateLimitFilter` конкретного обработчика — тогда будет использоваться он, а не значение из `RateLimitTool`.

## Переопределение storage и answer_callback в фильтре

`storage` и `answer_callback` можно передать напрямую в экземпляр `RateLimitFilter` — в этом случае они становятся атрибутами именно этого фильтра и действуют только на его обработчик, не затрагивая остальные:

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.storage import AsyncRedisLockStorage


@dp.message(
    Command("secret"),
    RateLimitFilter(
        rate_limit=SlidingWindowRateLimit(
            requests=2,
            time=timedelta(seconds=30)
        ),
        storage=AsyncRedisLockStorage(redis=AsyncRedis()),  # своё хранилище
        answer_callback=RateLimitAnswer(),                  # свой ответ
        key="secret_cmd"                                    # свой ключ
    ),
)
async def secret_handler(message: Message):
    await message.answer("Лимит: 2 запроса в 30 секунд.")
```

## Хранилища

Лимиты хранятся в `BaseLockStorage` — хранилище с поддержкой блокировок:

| Хранилище | Описание |
|---|---|
| `MemoryLockStorage` | **По умолчанию.** Данные в памяти процесса; сбрасываются при перезапуске |
| `FileLockStorage` | Данные в файле (`file=путь`); переживают перезапуск |
| `AsyncRedisLockStorage` | Данные в Redis (`redis=AsyncRedis(...)`); подходят для нескольких инстансов бота |

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.storage import AsyncRedisLockStorage


rate_limit_tool = RateLimitTool(
    storage=AsyncRedisLockStorage(redis=AsyncRedis())
)
aiogram_tool_setup(dp, [rate_limit_tool])
```

> [!TIP]
> Для горизонтального масштабирования (несколько экземпляров бота) используйте `AsyncRedisLockStorage` — блокировки и счётчики будут общими.

## Справочник API

`function: aiogram_tool_setup`

    arguments:
        dispatcher: Dispatcher - (required)
        tools: Iterable[BaseTool] - (required)

    Главная функция регистрации инструментов. Для rate limiting передайте
    экземпляр класса RateLimitTool в списке tools.


`class: RateLimitTool`

    arguments:
        storage: BaseLockStorage - (default MemoryLockStorage())
        answer_callback: RateLimitAnswer - (default RateLimitAnswer())

    Хранит настройки по умолчанию (storage и answer_callback) для всех
    обработчиков. При вызове setup сохраняет себя в
    dispatcher.workflow_data["rate_limit"], откуда его получают фильтры.

    Документация аргументов:

    1. storage — хранилище лимитов по умолчанию для всех обработчиков.

    2. answer_callback — ответ при превышении лимита по умолчанию
    для всех обработчиков.


`class: RateLimitFilter`

    arguments:
        rate_limit: BaseRateLimit - (required)
        storage: BaseLockStorage - (default None)
        answer_callback: RateLimitAnswer - (default None)
        key: str - (default None)
        all_users: bool - (default False)

    Фильтр ограничения частоты вызова обработчика. Возвращает True, если
    запрос разрешён, и False — если лимит исчерпан (перед этим вызывается
    answer_callback).

    Документация аргументов:

    1. rate_limit — алгоритм ограничения: FixedWindowRateLimit,
    SlidingWindowRateLimit, TokenBucketRateLimit или свой класс
    на базе BaseRateLimit.

    2. storage — хранилище для этого обработчика. Переданные в фильтр
    значения становятся его атрибутами и имеют приоритет над значениями
    из RateLimitTool. Если None — берётся storage из RateLimitTool.

    3. answer_callback — ответ для этого обработчика. Аналогично storage:
    аргумент фильтра имеет приоритет над RateLimitTool. Если None —
    берётся answer_callback из RateLimitTool.

    4. key — ключ для идентификации лимита. По умолчанию используется
    "модуль.имя_обработчика" (module.qualname).

    5. all_users — если True, лимит общий для всех пользователей,
    а не персональный.


`class: RateLimitAnswer`

    arguments (метод __call__):
        event: TelegramObject - (required)
        window_time: timedelta - (required)
        retry_after: timedelta - (required)

    Ответ по умолчанию при превышении лимита: отправляет текст
    "Next request after {retry_after} seconds.".

    Для кастомного ответа унаследуйтесь от класса и переопределите
    async __call__.


`class: BaseRateLimit`

    Базовый абстрактный класс алгоритмов ограничения.

    Атрибуты:
        storage_prefix: str - префикс ключей в хранилище
        ("fixed_aiot_rate_limit", "sliding_aiot_rate_limit",
        "token_bucket_aiot_rate_limit")

    Методы:
        build_key(event, unique_handler_name, all_users, key) - строит ключ
        вида "{storage_prefix}@{user_id | "users"}@{key | handler_name}"
        execute(event, storage, answer_callback, key) - абстрактный метод:
        проверяет лимит и возвращает bool

    Для собственного алгоритма унаследуйтесь от BaseRateLimit
    и реализуйте execute.


`class: FixedWindowRateLimit`

    arguments:
        requests: int - (required)
        time: timedelta - (required)

    Фиксированное окно: не более requests запросов за time.
    requests <= 0 — ValueError.


`class: SlidingWindowRateLimit`

    arguments:
        requests: int - (required)
        time: timedelta - (required)

    Скользящее окно: не более requests запросов за любые time.
    requests <= 0 — ValueError.


`class: TokenBucketRateLimit`

    arguments:
        bucket_size: int - (required)
        current_tokens: int - (default 1)
        refill_time: timedelta - (default timedelta(seconds=1))
        refill_tokens: int - (default 1)

    Токеновое ведро: bucket_size — максимум токенов, current_tokens —
    начальное число токенов, refill_tokens пополняются каждые refill_time.
    bucket_size, current_tokens, refill_tokens <= 0 — ValueError.


`class: UserLimit`

    arguments:
        requests: int | float - (required)
        time: datetime - (required)

    Дата-класс для хранения состояния лимита в хранилище (сериализуется
    в JSON). Используется алгоритмами FixedWindow и TokenBucket.


## Исключения

| Исключение | Когда выбрасывается |
|---|---|
| `ValueError` | Некорректные аргументы алгоритма: `requests <= 0` (Fixed/Sliding Window), `bucket_size`/`current_tokens`/`refill_tokens <= 0` (Token Bucket) |
| `ValueError("Dispatcher not found")` | В данных апдейта не найден диспетчер (см. примечание ниже) |
| `ValueError("Not found RateLimitTool. Call setup function")` | `RateLimitFilter` используется без зарегистрированного `RateLimitTool` |
| `TypeError` | Событие не имеет атрибута `from_user` |


> [!CAUTION]
> Фильтр получает `RateLimitTool` через диспетчер, который ищется в данных апдейта. При стандартном polling это работает автоматически. Если вы обрабатываете апдейты вручную (например, webhook через `feed_update`), передайте именованный аргумент `dispatcher=экземпляр класса Dispatcher`, иначе фильтр выбросит `ValueError("Dispatcher not found")`.


[Со всеми примерами кода можно ознакомиться здесь](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/)