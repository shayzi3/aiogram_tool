from typing import Callable, ParamSpec, TypeVar
from functools import wraps

from ..types.schema import ScopeObject
from ..types.enums import Scope


P = ParamSpec("P")
R = TypeVar("R")



def dependency_scope(scope: Scope) -> Callable[[Callable[P, R]], Callable[P, R]]:
     def decorator(obj: Callable[P, R]) -> Callable[P, R]:
          @wraps(obj)
          def wrapper() -> ScopeObject:
               return ScopeObject(
                    obj=obj,
                    scope=scope
               )
          return wrapper
     return decorator