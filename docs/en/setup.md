# aiogram_tool_setup

`aiogram_tool_setup` is the main entry point of the library. It registers all tools on the aiogram dispatcher and must be called **before** starting polling / webhooks.

- **Module:** `aiogram_tool.tools.setup`
- **Requirements:** Python 3.11+, aiogram 3.x

## Signature

```python
def aiogram_tool_setup(
    dispatcher: Dispatcher,
    tools: Iterable[BaseTool],
) -> None:
    """Main function for registering all tools"""
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `dispatcher` | `aiogram.Dispatcher` | The aiogram 3.x dispatcher instance the tools will be registered on |
| `tools` | `Iterable[BaseTool]` | An iterable (usually a list) of tools implementing the `BaseTool` interface |

The function returns nothing (`None`).

## BaseTool

All library tools inherit from the abstract base class:

```python
class BaseTool(ABC):
    @abstractmethod
    def setup(self, dispatcher: Dispatcher) -> None:
        raise NotImplementedError
```

To write your own tool, implement the `setup` method, which subscribes filters/middlewares on the dispatcher:

```python
from aiogram import Dispatcher
from aiogram_tool.tools.setup import BaseTool


class MyTool(BaseTool):
    def setup(self, dispatcher: Dispatcher) -> None:
        # e.g. dispatcher.message.outer_middleware(...)
        ...
```

## Validation

- `dispatcher` is not an instance of `Dispatcher` → `TypeError("Invalid type for dispatcher")`
- An item from `tools` is not an instance of `BaseTool` → `TypeError(f"Invalid type for tool {tool}")`

Tools are invoked in the order they appear in the iterable.

## Available tools

| Tool | Import | Purpose |
|---|---|---|
| `DependTool` | `aiogram_tool.tools.depend` | FastAPI-style dependency injection |
| `RateLimitTool` | `aiogram_tool.tools.limit` | Rate limiting for handlers |
| `LongCallbackData` / `CallbackDataAnswer` | `aiogram_tool.tools.callback_data` | Bypassing the 64-byte `callback_data` limit (used as a base class, see the callback_data documentation) |

Details: [depend.md](depend.md), [limit.md](limit.md), [callback_data.md](callback_data.md).

## Examples

### Basic usage

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

### With custom infrastructure

Many tools accept constructor parameters (e.g. a storage or a scope registry) that are passed before `setup` is called:

```python
from redis.asyncio import Redis as AsyncRedis

from aiogram_tool.tools.setup import aiogram_tool_setup
from aiogram_tool.tools.depend import DependTool, ScopeRegistry
from aiogram_tool.tools.limit import RateLimitTool
from aiogram_tool.storage import AsyncRedisLockStorage

scope_registry = ScopeRegistry()
redis = AsyncRedis()

aiogram_tool_setup(
    dp,
    [
        DependTool(scope_registry=scope_registry),
        RateLimitTool(storage=AsyncRedisLockStorage(redis=redis)),
    ],
)
```

> See the documentation of the corresponding tool for tool constructor signatures.

### Registering multiple instances

The order in the list determines the registration order on the dispatcher:

```python
aiogram_tool_setup(dp, [RateLimitTool(...), DependTool(...)])
```

## Errors

```python
aiogram_tool_setup(bot, [DependTool()])
# TypeError: Invalid type for dispatcher

aiogram_tool_setup(dp, [SomeRandomObject()])
# TypeError: Invalid type for tool <SomeRandomObject ...>
```
