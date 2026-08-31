from abc import ABC, abstractmethod
from collections.abc import Iterable

from aiogram import Dispatcher


class BaseTool(ABC):
    @abstractmethod
    def setup(self, dispatcher: Dispatcher) -> None:
        raise NotImplementedError


def aiogram_tool_setup(
    dispatcher: Dispatcher,
    tools: Iterable[BaseTool],
) -> None:
    """Main function for registering all tools"""

    if not isinstance(dispatcher, Dispatcher):
        raise TypeError("Invalid type for dispatcher")

    for tool in tools:
        if not isinstance(tool, BaseTool):
            raise TypeError(f"Invalid type for tool {tool}")
        tool.setup(dispatcher=dispatcher)
