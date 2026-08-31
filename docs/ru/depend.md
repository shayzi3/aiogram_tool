# Depends — внедрение зависимостей (Dependency Injection)

Инструмент для внедрения зависимостей в обработчики [aiogram 3.x](https://github.com/aiogram/aiogram) по принципу, похожему на `Depends()` из FastAPI.

Поддерживает функции, классы, class-functor'ы, async-генераторы (контекст-менеджеры), вложенные зависимости (sub-dependencies), scopes (`SINGLETON`, `REQUEST`, `TRANSIENT`), переопределение зависимостей для тестов и отмену вызова обработчика через `DependExit`.

## Как это работает?

- `DependTool` регистрирует два middleware для каждого типа апдейтов: `DependOuterMiddleware` и `DependInnerMiddleware`.
- `DependOuterMiddleware` создаёт «транзакцию» на каждый запрос: реестр зависимостей (`request_registry`) и стек контекст-менеджеров (`request_stack`). Также он добавляет в `data` аргумент `context` — текущее событие (`TelegramObject`).
- `DependInnerMiddleware` перед вызовом обработчика разбирает сигнатуру его функции и подставляет результаты зависимостей для аргументов, помеченных `Depends(...)`.

## Быстрый старт

```python
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_tool.tools.depend import Depends, DependTool
from aiogram_tool.tools.setup import aiogram_tool_setup

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


async def get_user_name(context: Message) -> str:
    # Аргументы без значений по умолчанию берутся из middleware_data
    return context.from_user.full_name


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    name: str = Depends(get_user_name),
):
    await message.answer(f"Привет, {name}!")


async def main():
    aiogram_tool_setup(dp, [DependTool()])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Объявление зависимости в обработчике

Есть два способа:

**1. Через значение по умолчанию:**

```python
@dp.message(CommandStart())
async def start_handler(message: Message, name: str = Depends(get_user_name)): ...
```

**2. Через `Annotated`:**

```python
from typing import Annotated


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    name: Annotated[str, Depends(get_user_name)],
): ...
```

## Поддерживаемые типы зависимостей

| Тип | Пример | Поведение |
|---|---|---|
| async-функция | `async def dep(): ...` | Результат `await`-ится и передаётся в обработчик |
| sync-функция | `def dep(): ...` | Вызывается как обычная функция |
| class-functor | объект с `async def __call__(self, ...)` | Вызывается как функция |
| класс | `Depends(BotToken)` | Создаётся экземпляр класса: аргументы `__init__` разрешаются как у обычной зависимости |
| async-генератор | `async def dep(): yield ...` | Работает как контекст-менеджер: код до `yield` — инициализация, после — очистка ресурсов |
| `@asynccontextmanager` | — | Аналогично async-генератору |

> [!CAUTION]
> Sync-генераторы и sync контекст-менеджеры не поддерживаются — будет выброшено `ContextManagerError`. Используйте `async def` или `@asynccontextmanager`.

Пример с классами:

```python
from aiogram import Bot
from aiogram_tool.tools.depend import ScopeRegistry, Scope

scope_registry = ScopeRegistry()


# Class-functor как зависимость
class CounterService:
    def __init__(self) -> None:
        self.count = 0

    async def __call__(self, context: Message) -> dict:
        self.count += 1
        return {"user_id": context.from_user.id, "current_count": self.count}


counter_instance = CounterService()
scope_registry.register(counter_instance, Scope.REQUEST)


# Класс как зависимость: аргументы __init__ внедряются автоматически
class BotToken:
    def __init__(self, bot: Bot) -> None:
        self.token = bot.token


scope_registry.register(BotToken, Scope.SINGLETON)


@dp.message(CommandStart())
async def start_handler(message: Message, stats: dict = Depends(counter_instance)):
    await message.answer(f"Нажато: {stats['current_count']} раз")


@dp.message(Command("token"))
async def token_handler(message: Message, bot_token: BotToken = Depends(BotToken)):
    await message.answer(f"Токен: {bot_token.token}")
```

## Откуда берутся аргументы зависимости

- Аргументы **без значения по умолчанию** берутся из `middleware_data` — это все данные, которые aiogram передаёт в обработчик. Если аргумент не найден — `InvalidMiddlewareDataArgumentError`.
- Аргументы **со значением по умолчанию** получают дефолт, если в `middleware_data` нет значения с таким же именем (данные из `middleware_data` имеют приоритет).
- Аргументы, помеченные `Depends(...)`, разрешаются рекурсивно — это вложенные зависимости.

> [!CAUTION]
> Не поддерживаются: `*args`, `**kwargs` и positional-only аргументы — будет выброшено `UnsupportedParameterKindError`.

## Вложенные зависимости (sub-dependencies)

Зависимости могут зависеть от других зависимостей:

```python
async def get_db_session():
    yield "DB_SESSION"


async def get_user_message(
    context: Message,
    db_session: str = Depends(get_db_session),
):
    return f"{context.from_user.username} session for you {db_session}"


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    user_message: Annotated[str, Depends(get_user_message)],
):
    await message.answer(user_message)
```

Циклические цепочки зависимостей обнаруживаются и приводят к `DependRecursionError`.

## Scopes (время жизни зависимости)

| Scope | Описание |
|---|---|
| `Scope.TRANSIENT` | **По умолчанию.** Зависимость вызывается каждый раз |
| `Scope.REQUEST` | Результат кэшируется на время обработки одного апдейта |
| `Scope.SINGLETON` | Результат кэшируется на всё время работы приложения |

Задать scope можно двумя способами:

**1. Через `ScopeRegistry`** (декоратором или методом `register`):

```python
import secrets

from aiogram_tool.tools.depend import ScopeRegistry, Scope

scope_registry = ScopeRegistry()


@scope_registry(Scope.SINGLETON)
async def get_app_config() -> str:
    return "APP_CONFIG_V1"


@scope_registry(Scope.REQUEST)
async def get_request_id() -> int:
    return secrets.randbits(20)


# или явно
scope_registry.register(some_func, Scope.TRANSIENT)
```

**2. Напрямую в `Depends`:**

```python
@dp.message(CommandStart())
async def start_handler(
    message: Message,
    config: str = Depends(get_app_config, scope=Scope.SINGLETON),
): ...
```

> [!TIP]
> Scope, переданный в `Depends`, имеет приоритет над scope, зарегистрированным в `ScopeRegistry`.

> [!TIP]
> `SINGLETON`-зависимости, являющиеся контекст-менеджерами, закрываются при остановке бота: `DependTool` регистрирует shutdown-хук на диспетчере.

Не забудьте передать свой `ScopeRegistry` в `DependTool`:

```python
aiogram_tool_setup(dp, [DependTool(scope_registry=scope_registry)])
```

## Переопределение зависимостей (dependency_override)

Позволяет подменить реализацию зависимости — удобно для тестов и локальной разработки:

```python
async def get_external_data():
    return "REAL_API_DATA"


async def get_mocked_data():
    return "MOCKED_DATA"


@dp.message(CommandStart())
async def start_handler(message: Message, data: str = Depends(get_external_data)):
    # Будет использован MOCKED_DATA из-за override
    await message.answer(f"Data received: {data}")


depend_tool = DependTool(
    dependency_override={
        get_external_data: Depends(get_mocked_data),
    }
)
```

Ключ — оригинальная зависимость (callable), значение — результат `Depends(...)`. Иначе будет выброшено `DependencyOverrideError`.

## DependExit — отмена вызова обработчика

Если зависимость выбрасывает исключение `DependExit`, обработчик вызван не будет:

```python
from aiogram_tool.tools.depend import DependExit


async def verify_user_access(context: Message) -> None:
    if context.from_user.id != 123456789:
        await context.answer("You are not admin!")
        raise DependExit()


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    _=Depends(verify_user_access),
):
    await message.answer("Welcome admin!")
```

## DependFilter — зависимости на уровне фильтров

`DependFilter` выполняет зависимости на этапе фильтров: если зависимость выбрасывает `DependExit`, фильтр возвращает `False` и обработчик не вызывается.

```python
from aiogram_tool.tools.depend import DependFilter


@dp.message(
    CommandStart(),
    DependFilter(Depends(verify_user_access)),
)
async def start_handler(message: Message):
    await message.answer("Welcome admin!")
```

> [!CAUTION]
> `DependFilter` требует зарегистрированного `DependTool` (он ищется в `dispatcher.workflow_data`), иначе будет выброшено `NotFoundDependTool`.

## Справочник API

`function: aiogram_tool_setup`

    arguments:
        dispatcher: Dispatcher - (required)
        tools: Iterable[BaseTool] - (required)

    Главная функция регистрации инструментов. Для DI передайте экземпляр
    класса DependTool в списке tools.


`class: DependTool`

    arguments:
        dependency_override: dict[Callable, From] - (default None)
        allowed_updates: list[str] - (default None)
        scope_registry: ScopeRegistry - (default None)

    Инструмент внедрения зависимостей. При вызове setup регистрирует
    outer/inner middleware для каждого типа апдейта и сохраняет себя
    в dispatcher.workflow_data["depend_tool"].

    Документация аргументов:

    1. dependency_override — словарь подмены зависимостей:
    {оригинальная_зависимость: Depends(новая_зависимость)}.

    2. allowed_updates — список типов апдейтов, для которых регистрируются
    middleware. По умолчанию берутся все используемые апдейты диспетчера
    (resolve_used_update_types).

    3. scope_registry — реестр scopes. По умолчанию создаётся пустой ScopeRegistry.


`function: Depends`

    arguments:
        depend: Callable - (required)
        scope: Scope - (опционально, keyword-only)

    Фабрика зависимостей. Возвращает объект From, который указывает middleware,
    что в этот аргумент нужно внедрить результат вызова depend.


`class: From`

    arguments:
        depend: Callable - (required)
        scope: Scope | _MISSING - (default _MISSING)

    Дата-класс, создаваемый функцией Depends. Если depend не является
    callable — будет выброшено CallableError.


`class: DependExit`

    Исключение. Если выброшено внутри зависимости, обработчик не будет
    вызван (inner middleware вернёт управление без вызова обработчика),
    а DependFilter вернёт False.


`class: DependFilter`

    arguments:
        *dependencies: From - (required)

    Фильтр, выполняющий зависимости на этапе фильтров обработчика.
    Если любая зависимость выбросит DependExit — фильтр вернёт False.
    Если передан объект, не являющийся From — InvalidDependencyError.


`class: ScopeRegistry`

    Реестр scopes зависимостей.

    Методы:
        register(obj: Callable, scope: Scope) - регистрирует scope для зависимости
        __call__(scope: Scope) - декоратор: @scope_registry(Scope.SINGLETON)
        get_scope(obj: Callable) - возвращает зарегистрированный scope
        get_scope_object(depend: From) - возвращает итоговый scope зависимости


`class: Scope`

    Enum со значениями:
        TRANSIENT - зависимость вызывается каждый раз (по умолчанию)
        REQUEST - результат кэшируется на время обработки одного апдейта
        SINGLETON - результат кэшируется на всё время работы приложения


## Исключения

| Исключение | Когда выбрасывается |
|---|---|
| `CallableError` | Зависимость в `From`/`Depends` не является callable |
| `DependencyOverrideError` | Некорректный ключ или значение в `dependency_override` |
| `ObserverError` | Неизвестный тип апдейта в `allowed_updates` |
| `UnsupportedParameterKindError` | Зависимость использует `*args`, `**kwargs` или positional-only аргументы |
| `InvalidMiddlewareDataArgumentError` | Аргумент зависимости без дефолта не найден в `middleware_data` |
| `DependRecursionError` | Обнаружена циклическая цепочка зависимостей |
| `ContextManagerError` | Используется sync-генератор или sync контекст-менеджер |
| `InvalidDependencyError` | В `DependFilter` передан объект, не являющийся `From` |
| `NotFoundDependTool` | `DependFilter` используется без зарегистрированного `DependTool` |


[Со всеми примерами кода можно ознакомиться здесь](https://github.com/shayzi3/aiogram_tool/blob/master/examples/depend/)