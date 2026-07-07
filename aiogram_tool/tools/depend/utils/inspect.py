import inspect

from typing import Callable, _AnnotatedAlias

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.schema import ScopeObject
from aiogram_tool.tools.depend.types.enums import Scope



def get_scope_object(depend: From) -> ScopeObject:
     scope_object = ScopeObject(
          depend=depend.depend,
          scope=Scope.REQUEST
     )
     if getattr(depend.depend, "dependency_scope", None):
          scope_object.scope = getattr(depend.depend, "dependency_scope")
           
     if depend.scope is not None:
          scope_object.scope = depend.scope
     return scope_object


def get_depends(
     obj: Callable, 
     dependency_override: dict[Callable, From] | None = None
) -> dict[str, ScopeObject]:
     signature = inspect.signature(obj)
          
     handler_depends = {}
     for param_name, param_meta in signature.parameters.items():
          if isinstance(param_meta.annotation, _AnnotatedAlias):
               annotated_metas = getattr(param_meta.annotation, "__metadata__", [])
               for meta in annotated_metas:
                    if isinstance(meta, From):
                         if dependency_override:
                              if meta.depend in dependency_override.keys():
                                   meta = dependency_override[meta.depend]
                         handler_depends[param_name] = get_scope_object(meta)
                         
          if isinstance(param_meta.default, From):
               default = param_meta.default
               if dependency_override:
                    if default.depend in dependency_override.keys():
                         default = dependency_override[default.depend]
               handler_depends[param_name] = get_scope_object(default)
     return handler_depends
     

def extract_call_object(obj: Callable) -> Callable:
     if any(
          [
               inspect.isfunction(obj),
               inspect.isclass(obj)
          ]
     ):
          return obj
     return getattr(obj, "__call__")  
     