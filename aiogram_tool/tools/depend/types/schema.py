from typing import Callable
from dataclasses import dataclass

from .enums import Scope


@dataclass
class ScopeObject:
     depend: Callable
     scope: Scope