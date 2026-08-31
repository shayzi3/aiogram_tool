# Depends — dependency injection

A tool for injecting dependencies into [aiogram 3.x](https://github.com/aiogram/aiogram) handlers, following a principle similar to `Depends()` from FastAPI.

It supports functions, classes, class-functors, async generators (context managers), nested dependencies (sub-dependencies), scopes (`SINGLETON`, `REQUEST`, `TRANSIENT`), dependency overriding for tests, and canceling handler invocation via `DependExit`.

## How does it work?

- `DependTool` registers two middlewares for each update type: `DependOuterMiddleware` and `DependInnerMiddleware`.
- `DependOuterMiddleware` creates a "transaction" for each request: a dependency registry (`request_registry`) and a stack of context managers (`request_stack`). It also adds the `context` argument to `data` — the current event (`TelegramObject`).
- `DependInnerMiddleware`, before calling the handler, parses its function signature and substitutes the results of dependencies for arguments marked with `Depends(...)`.

## Quick start

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
    # Arguments without default values are taken from middleware_data
    return context.from_user.full_name


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    name: str = Depends(get_user_name),
):
    await message.answer(f"Hello, {name}!")


async def main():
    aiogram_tool_setup(dp, [DependTool()])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## Declaring a dependency in a handler

There are two ways:

**1. Via a default value:**

```python
@dp.message(CommandStart())
async def start_handler(message: Message, name: str = Depends(get_user_name)):
    ...
```

**2. Via `Annotated`:**

```python
from typing import Annotated


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    name: Annotated[str, Depends(get_user_name)],
):
    ...
```

## Supported dependency types

| Type | Example | Behavior |
|---|---|---|
| async function | `async def dep(): ...` | The result is awaited and passed to the handler |
| sync function | `def dep(): ...` | Called as a regular function |
| class-functor | an object with `async def __call__(self, ...)` | Called as a function |
| class | `Depends(BotToken)` | A class instance is created: the `__init__` arguments are resolved like those of a regular dependency |
| async generator | `async def dep(): yield ...` | Works as a context manager: the code before `yield` — initialization, after — resource cleanup |
| `@asynccontextmanager` | — | Same as an async generator |

> [!CAUTION]
> Sync generators and sync context managers are not supported — a `ContextManagerError` will be raised. Use `async def` or `@asynccontextmanager`.

Example with classes:

```python
from aiogram import Bot
from aiogram_tool.tools.depend import ScopeRegistry, Scope

scope_registry = ScopeRegistry()


# Class-functor as a dependency
class CounterService:
    def __init__(self) -> None:
        self.count = 0

    async def __call__(self, context: Message) -> dict:
        self.count += 1
        return {"user_id": context.from_user.id, "current_count": self.count}


counter_instance = CounterService()
scope_registry.register(counter_instance, Scope.REQUEST)


# Class as a dependency: the __init__ arguments are injected automatically
class BotToken:
    def __init__(self, bot: Bot) -> None:
        self.token = bot.token


scope_registry.register(BotToken, Scope.SINGLETON)


@dp.message(CommandStart())
async def start_handler(message: Message, stats: dict = Depends(counter_instance)):
    await message.answer(f"Pressed: {stats['current_count']} times")


@dp.message(Command("token"))
async def token_handler(message: Message, bot_token: BotToken = Depends(BotToken)):
    await message.answer(f"Token: {bot_token.token}")
```

## Where dependency arguments come from

- Arguments **without a default value** are taken from `middleware_data` — this is all the data that aiogram passes to the handler. If an argument is not found — `InvalidMiddlewareDataArgumentError`.
- Arguments **with a default value** receive the default if `middleware_data` contains no value with the same name (data from `middleware_data` takes priority).
- Arguments marked with `Depends(...)` are resolved recursively — these are nested dependencies.

> [!CAUTION]
> Not supported: `*args`, `**kwargs`, and positional-only arguments — an `UnsupportedParameterKindError` will be raised.

## Nested dependencies (sub-dependencies)

Dependencies can depend on other dependencies:

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

Cyclic dependency chains are detected and lead to a `DependRecursionError`.

## Scopes (dependency lifetime)

| Scope | Description |
|---|---|
| `Scope.TRANSIENT` | **Default.** The dependency is called every time |
| `Scope.REQUEST` | The result is cached for the duration of processing a single update |
| `Scope.SINGLETON` | The result is cached for the entire lifetime of the application |

A scope can be set in two ways:

**1. Via `ScopeRegistry`** (with a decorator or the `register` method):

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


# or explicitly
scope_registry.register(some_func, Scope.TRANSIENT)
```

**2. Directly in `Depends`:**

```python
@dp.message(CommandStart())
async def start_handler(
    message: Message,
    config: str = Depends(get_app_config, scope=Scope.SINGLETON),
):
    ...
```

> [!TIP]
> A scope passed to `Depends` takes priority over a scope registered in `ScopeRegistry`.

> [!TIP]
> `SINGLETON` dependencies that are context managers are closed when the bot stops: `DependTool` registers a shutdown hook on the dispatcher.

Don't forget to pass your `ScopeRegistry` to `DependTool`:

```python
aiogram_tool_setup(dp, [DependTool(scope_registry=scope_registry)])
```

## Dependency overriding (dependency_override)

Allows replacing the implementation of a dependency — convenient for tests and local development:

```python
async def get_external_data():
    return "REAL_API_DATA"


async def get_mocked_data():
    return "MOCKED_DATA"


@dp.message(CommandStart())
async def start_handler(message: Message, data: str = Depends(get_external_data)):
    # MOCKED_DATA will be used due to the override
    await message.answer(f"Data received: {data}")


depend_tool = DependTool(
    dependency_override={
        get_external_data: Depends(get_mocked_data),
    }
)
```

The key is the original dependency (callable), the value is the result of `Depends(...)`. Otherwise, a `DependencyOverrideError` will be raised.

## DependExit — canceling handler invocation

If a dependency raises the `DependExit` exception, the handler will not be called:

```python
from aiogram_tool.tools.depend import DependExit


async def verify_user_access(context: Message) -> None:
    if context.from_user.id != 123456789:
        await context.answer("You are not admin!")
        raise DependExit()


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    _ = Depends(verify_user_access),
):
    await message.answer("Welcome admin!")
```

## DependFilter — filter-level dependencies

`DependFilter` executes dependencies at the filter stage: if a dependency raises `DependExit`, the filter returns `False` and the handler is not called.

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
> `DependFilter` requires a registered `DependTool` (it is looked up in `dispatcher.workflow_data`), otherwise a `NotFoundDependTool` will be raised.

## API reference

`function: aiogram_tool_setup`

    arguments:
        dispatcher: Dispatcher - (required)
        tools: Iterable[BaseTool] - (required)

    The main function for registering tools. For DI, pass an instance
    of the DependTool class in the tools list.


`class: DependTool`

    arguments:
        dependency_override: dict[Callable, From] - (default None)
        allowed_updates: list[str] - (default None)
        scope_registry: ScopeRegistry - (default None)

    The dependency injection tool. When setup is called, it registers
    outer/inner middlewares for each update type and stores itself
    in dispatcher.workflow_data["depend_tool"].

    Argument documentation:

    1. dependency_override — a dictionary for overriding dependencies:
    {original_dependency: Depends(new_dependency)}.

    2. allowed_updates — a list of update types for which the middlewares
    are registered. By default, all update types used by the dispatcher
    are taken (resolve_used_update_types).

    3. scope_registry — the scope registry. By default, an empty ScopeRegistry is created.


`function: Depends`

    arguments:
        depend: Callable - (required)
        scope: Scope - (optional, keyword-only)

    The dependency factory. Returns a From object that tells the middleware
    to inject the result of calling depend into this argument.


`class: From`

    arguments:
        depend: Callable - (required)
        scope: Scope | _MISSING - (default _MISSING)

    A dataclass created by the Depends function. If depend is not
    callable — a CallableError will be raised.


`class: DependExit`

    An exception. If raised inside a dependency, the handler will not
    be called (the inner middleware will return control without calling
    the handler), and DependFilter will return False.


`class: DependFilter`

    arguments:
        *dependencies: From - (required)

    A filter that executes dependencies at the handler's filter stage.
    If any dependency raises DependExit — the filter returns False.
    If an object that is not From is passed — InvalidDependencyError.


`class: ScopeRegistry`

    The registry of dependency scopes.

    Methods:
        register(obj: Callable, scope: Scope) - registers a scope for a dependency
        __call__(scope: Scope) - decorator: @scope_registry(Scope.SINGLETON)
        get_scope(obj: Callable) - returns the registered scope
        get_scope_object(depend: From) - returns the resulting scope of a dependency


`class: Scope`

    Enum with the values:
        TRANSIENT - the dependency is called every time (default)
        REQUEST - the result is cached for the duration of processing a single update
        SINGLETON - the result is cached for the entire lifetime of the application


## Exceptions

| Exception | When it is raised |
|---|---|
| `CallableError` | The dependency in `From`/`Depends` is not callable |
| `DependencyOverrideError` | An incorrect key or value in `dependency_override` |
| `ObserverError` | An unknown update type in `allowed_updates` |
| `UnsupportedParameterKindError` | The dependency uses `*args`, `**kwargs`, or positional-only arguments |
| `InvalidMiddlewareDataArgumentError` | A dependency argument without a default is not found in `middleware_data` |
| `DependRecursionError` | A cyclic dependency chain is detected |
| `ContextManagerError` | A sync generator or sync context manager is used |
| `InvalidDependencyError` | An object that is not `From` is passed to `DependFilter` |
| `NotFoundDependTool` | `DependFilter` is used without a registered `DependTool` |


[All code examples can be found here](examples/depend/)