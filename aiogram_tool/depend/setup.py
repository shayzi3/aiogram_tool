from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.dispatcher.event.handler import FilterObject


from .depend import Depend
from .components import DependFilter, StackMiddleware





def setup_depend_tool(
     dispatcher: Dispatcher,
     dependency_override: dict[str, Depend] = {},
     allowed_updates: list[str] = [],
) -> None:
     if not isinstance(dispatcher, Dispatcher):
          raise TypeError("Invalid type for dispatcher")
     
     if dependency_override:
          for dep in dependency_override.values():
               if not isinstance(dep, Depend):
                    raise TypeError("Invalid type in dependency_override")
          dispatcher["dependency_override"] = dependency_override     
               
     if allowed_updates:
          for allow in allowed_updates:
               if allow not in dispatcher.observers:
                    raise TypeError(f"Invalid observer {allow}")
               else:
                    observer: TelegramEventObserver = getattr(dispatcher, allow)
                    
                    if observer.handlers:
                         observer.outer_middleware(StackMiddleware())
                         for handler in observer.handlers:
                              handler.filters.append(FilterObject(DependFilter()))
     
     else:
          for allow in dispatcher.resolve_used_update_types():
               observer: TelegramEventObserver = getattr(dispatcher, allow)
               
               if observer.handlers:
                    observer.outer_middleware(StackMiddleware())
                    for handler in observer.handlers:
                         handler.filters.append(FilterObject(DependFilter()))
                    
               
               
     