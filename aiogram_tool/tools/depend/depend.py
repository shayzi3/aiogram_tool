from typing import Callable, Optional

from aiogram_tool.utils.inspect_signature import InspectSignature
from aiogram_tool.tools.depend.types.schema import ScopeObject
from aiogram_tool.tools.depend.types.enums import Scope
     


class Depends:
     
     def __init__(self, obj: Callable, scope: Optional[Scope] = None) -> None:
          self.signature = InspectSignature(obj)
          self.scope = scope
          
          if getattr(self.signature.obj, "is_dependency_scope_wrapped", None) is True:
               scope_object: ScopeObject = obj()
               if self.scope is None:
                    self.scope = scope_object.scope
               self.signature = InspectSignature(scope_object.obj)
          
          if self.scope is None:
               self.scope = Scope.REQUEST
          
     def __repr__(self) -> str:
          return f"{self.__class__.__name__}(obj={self.signature.obj}, scope={self.scope})"
          
     def __hash__(self) -> int:
          return hash(self.signature.obj)
     