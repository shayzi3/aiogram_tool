import inspect

from contextlib import (
     asynccontextmanager, 
     contextmanager,
     _AsyncGeneratorContextManager,
     _GeneratorContextManager
)
from typing import Callable, Any, _AnnotatedAlias



class Depend:
     def __init__(self, obj: Callable[[Any], Any]) -> None:
          self.isgenerator = False
          self.asyncfunc = False
          self.obj = obj
          
          
          if inspect.iscoroutinefunction(obj):
               self.asyncfunc = True
          
          else:
               if inspect.isasyncgenfunction(obj):
                    self.isgenerator = True
                    self.asyncfunc = True
                    self.obj = asynccontextmanager(obj)
               
               elif inspect.isgeneratorfunction(obj):
                    self.isgenerator = True
                    self.obj = contextmanager(obj)
                    
               else:
                    try:
                         if isinstance(obj(), _AsyncGeneratorContextManager):
                              self.isgenerator = True
                              self.asyncfunc = True
                              
                         elif isinstance(obj(), _GeneratorContextManager):
                              self.isgenerator = True
                    except:
                         pass
                    
          self.obj_name = obj.__name__
          self.arguments = {}
          
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
                    self.arguments[key] = annotation
                    
                    
     async def call(self, middleware_data: dict[str, Any]) -> Any:
          kwargs = {}
          for key, value in self.arguments.items():
               if isinstance(value, Depend):
                    kwargs[key] = await value.call(middleware_data)
               else:
                    try:
                         kwargs[key] = middleware_data[key]
                    except KeyError:
                         raise KeyError(f"key {key} not exists in middleware data")
          
          if self.asyncfunc is False:
               if self.isgenerator is True:
                    with self.obj(**kwargs) as generator:
                         return generator
               return self.obj(**kwargs)
               
          else:
               if self.isgenerator is True:
                    async with self.obj(**kwargs) as asgenerator:
                         return asgenerator
               return await self.obj(**kwargs)