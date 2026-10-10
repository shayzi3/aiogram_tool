# aiogram_tool_setup

`aiogram_tool_setup` — главная точка входа библиотеки. Она регистрирует все инструменты в диспетчере aiogram и должна вызываться **до** старта пуллинга / вебхуков.

## Сигнатура

```python
def aiogram_tool_setup(
    dispatcher: Dispatcher,
    tools: Iterable[BaseTool],
) -> None:
    """Main function for registering all tools"""
```

### Параметры

| Параметр | Тип | Описание |
|---|---|---|
| `dispatcher` | `aiogram.Dispatcher` | Экземпляр диспетчера aiogram 3.x, в котором будут зарегистрированы инструменты |
| `tools` | `Iterable[BaseTool]` | Итерируемый набор инструментов (обычно список), реализующих интерфейс `BaseTool` |

Функция ничего не возвращает (`None`).

## BaseTool

Все инструменты библиотеки наследуются от абстрактного базового класса:

```python
class BaseTool(ABC):
    @abstractmethod
    def setup(self, dispatcher: Dispatcher) -> None:
        raise NotImplementedError
```

Чтобы написать собственный инструмент, реализуйте метод `setup`, который сохраняет фильтры/мидлвари в диспетчере:

```python
from aiogram import Dispatcher
from aiogram_tool.tools.setup import BaseTool


class MyTool(BaseTool):
    def setup(self, dispatcher: Dispatcher) -> None:
        # например, dispatcher.message.outer_middleware(...)
        ...
```

Инструменты вызываются в порядке следования в итерируемом объекте.

## Доступные инструменты

| Инструмент | Импорт | Назначение |
|---|---|---|
| `DependTool` | `aiogram_tool.tools.depend` | Dependency injection в стиле FastAPI |
| `RateLimitTool` | `aiogram_tool.tools.limit` | Ограничение частоты вызовов хендлеров |
| `LongCallbackData` / `CallbackDataAnswer` | `aiogram_tool.tools.callback_data` | Обход лимита 64 байт для `callback_data` (используется как базовый класс, см. документацию callback_data) |

## Примеры

### Базовое использование

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

### С кастомной инфраструктурой

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

## Ошибки

```python
aiogram_tool_setup(bot, [DependTool()])
# TypeError: Invalid type for dispatcher

aiogram_tool_setup(dp, [SomeRandomObject()])
# TypeError: Invalid type for tool <SomeRandomObject ...>
```