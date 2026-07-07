from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver

from aiogram_tool.tools.setup import BaseTool
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransactionManager
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransactionManager
from .components.inner_middleware import DependInnerMiddleware
from .depend import From



class DependTool(BaseTool):
     
     def __init__(
          self,
          dependency_override: dict[str, From] = None,
          allowed_updates: list[str] = None,
     ) -> None:
          if dependency_override:
               for depend in dependency_override.values():
                    if not isinstance(depend, From):
                         raise ValueError(f"Invalid type in dependency_override {depend}")
          
          self.dependency_override = dependency_override
          self.allowed_updates = allowed_updates
          self.registry = DependRegistryTransactionManager()
          self.stack = AsyncExitStackTransactionManager()
          
     async def shutdown(self) -> None:
          await self.stack.aclose()
          
     def setup(self, dispatcher: Dispatcher) -> None:
          dispatcher.shutdown()(self.shutdown)
          
          middleware = DependInnerMiddleware(depend_tool=self)
          for update in self.allowed_updates or dispatcher.resolve_used_update_types():
               observer: TelegramEventObserver = dispatcher.observers.get(update, None)
               if observer is None:
                    raise ValueError(f"Invalid observer {update}")
               observer.middleware(middleware)
          