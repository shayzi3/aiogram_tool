from typing import Callable, ParamSpec, TypeVar

from aiogram_tool.tools.depend.types.enums import Scope


P = ParamSpec("P")
T = TypeVar("R")



def dependency_scope(scope: Scope) -> Callable[[Callable[P, T]], Callable[P, T]]:
     def wrapped(obj: Callable[P, T]) -> Callable[P, T]:
          obj.dependency_scope = scope
          return obj
     return wrapped