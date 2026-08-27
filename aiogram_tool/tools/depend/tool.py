from typing import Callable

from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver

from aiogram_tool.tools.setup import BaseTool
from aiogram_tool.tools.depend.utils.scope_registry import ScopeRegistry
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransactionManager
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransactionManager
from aiogram_tool.tools.depend.types.exceptions import ObserverError, DependencyOverrideError
from .components.inner_middleware import DependInnerMiddleware
from .components.outer_middleware import DependOuterMiddleware
from .depend import From



class DependTool(BaseTool):
     """Class for register dependency middlewares"""
     
     def __init__(
          self,
          dependency_override: dict[Callable, From] | None = None,
          allowed_updates: list[str] | None = None,
          scope_registry: ScopeRegistry | None = None
     ) -> None:
          if dependency_override is not None:
               for key, depend in dependency_override.items():
                    error_msg = None
                    if not callable(key):
                         error_msg = f"Key {key} in dependency override must be callable"

                    if not isinstance(depend, From):
                         error_msg = f"Invalid type in dependency_override {depend}"
                    
                    if error_msg is not None:
                         raise DependencyOverrideError(error_msg)
          
          self.dependency_override = dependency_override or {}
          self.allowed_updates = allowed_updates
          self.scope_registry = scope_registry or ScopeRegistry()
          self.registry = DependRegistryTransactionManager()
          self.stack_manager = AsyncExitStackTransactionManager()
          
     async def shutdown(self) -> None:
          await self.stack_manager.stack.aclose()
          
     def setup(self, dispatcher: Dispatcher) -> None:
          dispatcher.shutdown.register(self.shutdown)
          dispatcher.workflow_data["depend_tool"] = self
          
          updates = (
               self.allowed_updates 
               if self.allowed_updates is not None 
               else dispatcher.resolve_used_update_types()
          )
          inner_middleware = DependInnerMiddleware(depend_tool=self)
          outer_middleware = DependOuterMiddleware(depend_tool=self)
          
          for update in updates:
               observer: TelegramEventObserver = dispatcher.observers.get(update, None)
               if observer is None:
                    raise ObserverError(f"Invalid observer {update}")
               
               observer.outer_middleware(outer_middleware)
               observer.middleware(inner_middleware)
          