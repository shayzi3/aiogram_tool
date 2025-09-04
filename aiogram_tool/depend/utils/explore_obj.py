import inspect

from typing import Callable, _AnnotatedAlias
from contextlib import asynccontextmanager, contextmanager

from aiogram_tool import depend

     


class ExploreObj:
     def __init__(self, obj: Callable):
          self.obj = obj
          self.isgenerator = False
          self.isasync = False
          self.obj_parameters: dict[str, depend.Depend] = {}
          self.obj_name = getattr(obj, "__name__", "")
          
          if isinstance(self.obj, type):
               raise TypeError("dont valid type. Initialize class")
          
          if not callable(self.obj):
               raise TypeError("obj must be a callable")
          
          if not inspect.isfunction(self.obj):
               self.obj_name = self.obj.__class__.__name__
               self.obj = getattr(self.obj, "__call__")
               
          self.__rule_for_call_obj()
          self.__find_obj_parameters()
               
     
     def __rule_for_call_obj(self) -> None:
          if inspect.iscoroutinefunction(self.obj):
               self.isasync = True
               
          else:
               if inspect.isasyncgenfunction(self.obj):
                    self.isgenerator = True
                    self.isasync = True
                    self.obj = asynccontextmanager(self.obj)
                    
               elif inspect.isgeneratorfunction(self.obj):
                    self.isgenerator = True
                    self.obj = contextmanager(self.obj)
                    
                    
     def __find_obj_parameters(self) -> None:
          signature = inspect.signature(self.obj)
          for param, param_spec in signature.parameters.items():
               if isinstance(param_spec.annotation, _AnnotatedAlias):
                    types = getattr(param_spec.annotation, "__metadata__")
                    for dependency in types:
                         if isinstance(dependency, depend.Depend):
                              self.obj_parameters[param] = dependency
               else:
                    self.obj_parameters[param] = param_spec.default
                    