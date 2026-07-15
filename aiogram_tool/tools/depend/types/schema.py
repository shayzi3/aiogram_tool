from inspect import Signature
from typing import Any, Callable
from dataclasses import dataclass

from .enums import Scope


@dataclass(frozen=True)
class ScopeObject:
     depend: Callable
     scope: Scope
     

@dataclass(frozen=True)
class InspectArgument:
     name: str
     arg_kind: Any
     value: Any | ScopeObject | Signature.empty