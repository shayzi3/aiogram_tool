from typing import List, Dict, Optional, Union

from aiogram import Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver

from aiogram_tool.tools.setup import ToolProtocol
from aiogram_tool.storage import MemoryLimitStorage, MemoryStorage
from .depend import Depends



class DependTool(ToolProtocol):
     __tool__ = "dependency"
     
     def __init__(
          self,
          dependency_override: Optional[Dict[str, Depends]] = None,
          allowed_updates: Optional[List[str]] = None,
          storage: Optional[Union[MemoryLimitStorage, MemoryStorage]] = None
     ) -> None:
          if dependency_override:
               for depend in dependency_override.values():
                    if not isinstance(depend, Depends):
                         raise TypeError(f"Invalid type in dependency_override {depend}")
          
          if (storage is not None) and not isinstance(storage, (MemoryStorage, MemoryLimitStorage)):
               raise TypeError(f"Storage in DependTool must be only in memory")
          
          self.dependency_override = dependency_override
          self.allowed_updates = allowed_updates
          self.storage = storage
          
     
     def setup(
          self, 
          dispatcher: Dispatcher, 
          storage: Optional[Union[MemoryLimitStorage, MemoryStorage]] = None
     ) -> None:
          from .components import DependInnerMiddleware
          
          if self.storage is None:
               if not isinstance(storage, (MemoryStorage, MemoryLimitStorage)):
                    raise TypeError(f"Storage in DependTool must be only in memory")
               else:
                    self.storage = storage
          
          middleware = DependInnerMiddleware(depend_tool=self)
          if self.allowed_updates:
               for update in self.allowed_updates:
                    if update not in dispatcher.observers:
                         raise TypeError(f"Invalid observer {update}")
                    else:
                         observer: TelegramEventObserver = dispatcher.observers.get(update)
                         observer.middleware(middleware)
          else:
               for update in dispatcher.resolve_used_update_types():
                    observer: TelegramEventObserver = dispatcher.observers.get(update)
                    observer.middleware(middleware)
          