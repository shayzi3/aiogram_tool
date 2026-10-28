from collections.abc import Callable
from dataclasses import dataclass

from .enums import Scope


@dataclass(frozen=True)
class ScopeObject:
    depend: Callable
    scope: Scope
