import inspect

from typing import Callable, Any
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass

from .types_ import UNSET


@dataclass
class TypeHint:
     default: Any
     annotation: type | UNSET


class InspectSignature:
     def __init__(self, obj: Callable) -> None:
          if isinstance(obj, type):
               raise ValueError(f"support only instance of classess")
          
          if not callable(obj):
               raise ValueError(f"Object")
          
          self.obj = obj
          self.obj_name = getattr(obj, "__name__", "")
          self.is_generator = False
          self.is_async = False
          self.type_hints_with_default: dict[str, TypeHint] = {}
          
          if not inspect.isfunction(self.obj):
               call_method = getattr(self.obj, "__call__", None)
               if call_method is None:
                    raise ValueError(f"not found __call__ method at instance of class {obj}")
               else:
                    self.obj = call_method
                    self.obj_name = getattr(getattr(obj, "__class__"), "__name__")
          
          self.__inspect()
          
     def __inspect(self) -> None:
          type_hints_with_default = {}
          signature = inspect.signature(self.obj)
          for arg, arg_spec in signature.parameters.items():
               type_hints_with_default[arg] = TypeHint(
                    annotation=arg_spec.annotation,
                    default=(
                         UNSET if arg_spec.default is inspect._empty
                         else arg_spec.default
                    )
               )
          
          if type_hints_with_default:
               self.type_hints_with_default = type_hints_with_default
          
          if inspect.iscoroutinefunction(self.obj):
               self.is_async = True
          else:
               if inspect.isasyncgenfunction(self.obj):
                    self.is_generator = True
                    self.is_async = True
                    self.obj = asynccontextmanager(self.obj)
                    
               elif inspect.isgeneratorfunction(self.obj):
                    self.is_generator = True
                    self.obj = contextmanager(self.obj)
          
          
     