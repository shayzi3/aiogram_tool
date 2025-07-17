import inspect

from typing import Callable, Awaitable
from aiogram.types import Message
from aiogram import Dispatcher

from datetime import datetime, timedelta

from .storage.abstract_storage import AbstractStorage
from .storage import MemoryStorage



def setup_limit_tool(
     dispatcher: Dispatcher,
     storage: AbstractStorage = MemoryStorage(),
     answer_callback: Callable[[Message, timedelta, datetime], Awaitable] | None = None
) -> None:
     if not issubclass(type(storage), AbstractStorage):
          raise TypeError(f"Invalid type for storage")
     
     if answer_callback is not None:
          if not inspect.iscoroutinefunction(answer_callback):
               raise TypeError(f"answer_callback must be croutine function")
          
     dispatcher.__setitem__("storage", storage)
     dispatcher.__setitem__("answer_callback", answer_callback)