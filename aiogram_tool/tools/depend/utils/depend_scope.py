from typing import Callable, ParamSpec, TypeVar
from functools import wraps

from ..types.schema import ScopeObject
from ..types.enums import Scope


P = ParamSpec("P")
T = TypeVar("R")



def dependency_scope(scope: Scope) -> Callable[[Callable[P, T]], Callable[P, T]]:
     def decorator(func: Callable[P, T]) -> Callable[P, T]:
          @wraps(func)
          def wrapped() -> T:
               return ScopeObject(obj=func, scope=scope)
          wrapped.is_dependency_scope_wrapped = True
          return wrapped
     return decorator