from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver

from .depend import Depend
from .components.middleware import DependMiddleware





def setup_depend_tool(
     dispatcher: Dispatcher,
     dependency_override: dict[str, Depend] = {},
     allowed_updates: list[str] = [],
     middleware: bool = True,
) -> None:
     if not isinstance(dispatcher, Dispatcher):
          raise TypeError("dispatcher must be Dispatcher type")
     
     if dependency_override:
          for dep in dependency_override.values():
               if not isinstance(dep, Depend):
                    raise TypeError(f"Invalid type in dependency_override {dep}")
               
     if allowed_updates:
          for allow in allowed_updates:
               if allow not in dispatcher.observers:
                    raise TypeError(f"observer {allow} not exists")
     
     if middleware is True:
          for allow in dispatcher.resolve_used_update_types() or allowed_updates:
               observer: TelegramEventObserver = getattr(dispatcher, allow)
               observer.middleware(DependMiddleware())
     dispatcher.__setitem__("dependency_override", dependency_override)