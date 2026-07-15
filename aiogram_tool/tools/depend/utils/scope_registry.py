from typing import Callable, ParamSpec, TypeVar

from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.types.schema import ScopeObject
from aiogram_tool.tools.depend.depend import From
from aiogram_tool.types import _MISSING



P = ParamSpec("P")
T = TypeVar("T")


class ScopeRegistry:
     
     def __init__(self):
          self.scopes: dict[Callable, Scope] = {}
          
     def register(self, obj: Callable, scope: Scope) -> None:
          self.scopes[obj] = scope
          
     def __call__(self, scope: Scope) -> Callable[[Callable[P, T]], Callable[P, T]]:
          def wrapper(obj: Callable[P, T]) -> Callable[P, T]:
               self.register(obj, scope)
               return obj
          return wrapper
     
     def get_scope(self, obj: Callable) -> Scope | _MISSING:
          return self.scopes.get(obj, _MISSING)
     
     def get_scope_object(self, depend: From) -> ScopeObject:
          scope = Scope.TRANSIENT
          
          registry_scope = self.get_scope(depend.depend)
          if registry_scope is not _MISSING:
               scope = registry_scope
               
          if depend.scope is not _MISSING:
               scope = depend.scope
               
          return ScopeObject(
               depend=depend.depend,
               scope=scope
          )