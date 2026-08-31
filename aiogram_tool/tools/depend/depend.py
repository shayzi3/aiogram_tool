from collections.abc import Callable
from dataclasses import dataclass

from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.types.exceptions import CallableError
from aiogram_tool.types import _MISSING


@dataclass(frozen=True)
class From:
    depend: Callable
    scope: Scope | _MISSING = _MISSING

    def __post_init__(self) -> None:
        if not callable(self.depend):
            raise CallableError(f"object {self.depend} is not callable")


def Depends(depend: Callable, *, scope: Scope | _MISSING = _MISSING) -> From:
    return From(depend=depend, scope=scope)
