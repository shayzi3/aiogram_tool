import inspect

from contextlib import (
     asynccontextmanager, 
     contextmanager
)
from typing import (
     Callable, 
     Any, 
     _AnnotatedAlias
)



class Depend:
     def __init__(self, obj: Callable) -> None:
          self.obj = obj
          self.isgenerator = False
          self.isasync = False
          self.obj_name = getattr(obj, "__name__", "")
          self.arguments = {}
          
          if isinstance(self.obj, type):
               raise TypeError("dont valid type. Initialize class")
          
          if not callable(self.obj):
               raise TypeError("obj must be a callable")
          
          if not inspect.isfunction(self.obj):
               self.obj_name = self.obj.__class__.__name__
               self.obj = getattr(self.obj, "__call__")
                    
          self.__explore_obj()
          self.__explore_signature()
          
                    
     def __explore_obj(self) -> None:
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
                    
               else:
                    types = []
                    for closure in inspect.getclosurevars(self.obj):
                         if isinstance(closure, dict):
                              types.extend(list(closure.values()))

                    for type_ in types:
                         name = getattr(type_, "__name__", None)
                         if name == "_AsyncGeneratorContextManager":
                              self.isasync = True
                              self.isgenerator = True
                              
                         elif name == "_GeneratorContextManager":
                              self.isgenerator = True
                    
                    
     def __explore_signature(self) -> None:
          signature = inspect.signature(self.obj)
          for key, annotation in signature.parameters.items():
               default_value = annotation.default
               
               if isinstance(annotation.annotation, _AnnotatedAlias):
                    types = getattr(annotation.annotation, "__metadata__")
                    for type_ in types:
                         if isinstance(type_, Depend):
                              self.arguments[key] = type_
                              
               elif isinstance(default_value, Depend):
                    self.arguments[key] = default_value
                    
               else:
                    self.arguments[key] = annotation.annotation
                    
                    
     async def call(self, middleware_data: dict[str, Any]) -> Any:
          kwargs = {}
          for key, value in self.arguments.items():
               if isinstance(value, Depend):
                    kwargs[key] = await value.call(middleware_data)
               else:
                    kwargs[key] = middleware_data.get(key)

          if self.isasync is False:
               if self.isgenerator is True:
                    with self.obj(**kwargs) as generator:
                         return generator
               return self.obj(**kwargs)
               
          else:
               if self.isgenerator is True:
                    async with self.obj(**kwargs) as asgenerator:
                         return asgenerator
               return await self.obj(**kwargs)