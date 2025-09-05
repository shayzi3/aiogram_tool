from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver

from .depend import Depend
from .components import DependInnerMiddleware





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
          for update in allowed_updates:
               if update not in dispatcher.observers:
                    raise TypeError(f"Invalid observer {update}")
               else:
                    observer: TelegramEventObserver = dispatcher.observers.get(update)
                    observer.middleware(DependInnerMiddleware())
     
     else:
          for update in dispatcher.resolve_used_update_types():
               observer: TelegramEventObserver = dispatcher.observers.get(update)
               observer.middleware(DependInnerMiddleware())
               
               
                    
               
               
     