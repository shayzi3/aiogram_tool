import inspect

from typing import Callable, Any
from contextlib import AsyncExitStack

from .utils.explore_obj import ExploreObj
from .types.schema import ScopeObject
from .types.enums import Scope



class Depend(ExploreObj):
     app_container = {}
     
     def __init__(self, obj: Callable) -> None:
          self.scope = Scope.REQUEST

          explore_obj = obj
          if not inspect.iscoroutinefunction(obj):
               try:
                    scope_object = obj() 
                    if isinstance(scope_object, ScopeObject):
                         explore_obj = scope_object.obj
                         self.scope = scope_object.scope
               except:
                    pass
                    
          super().__init__(obj=explore_obj)
          
     async def call(
          self, 
          middleware_data: dict[str, Any],
          stack: AsyncExitStack
     ) -> Any:
          if self.scope == Scope.APP:
               if self.obj_name in self.app_container:
                    return self.app_container[self.obj_name]
          
          inject_obj_parameters = {}
          for key, value in self.obj_parameters.items():
               if isinstance(value, Depend):
                    inject_obj_parameters[key] = await value.call(middleware_data, stack)
                    
               elif value is inspect._empty:
                    inject_obj_parameters[key] = middleware_data.get(key, None)
                    
          obj_returning = None
          call_obj_with_params = self.obj(**inject_obj_parameters)
          if self.isasync is False:
               if self.isgenerator is True:
                    obj_returning = stack.enter_context(call_obj_with_params)
               else:
                    obj_returning = call_obj_with_params
          else:
               if self.isgenerator is True:
                    obj_returning = await stack.enter_async_context(call_obj_with_params)
               else:
                    obj_returning = await call_obj_with_params
                    
          if self.scope == Scope.APP:
               if self.obj_name not in self.app_container:
                    self.app_container[self.obj_name] = obj_returning
          return obj_returning