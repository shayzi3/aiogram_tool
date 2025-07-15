import inspect

from typing import Callable, Awaitable
from datetime import datetime, timedelta

from aiogram import Dispatcher
from aiogram.filters import Filter
from aiogram.types import Message

from .storage.abstract_storage import AbstractStorage
from .storage import MemoryStorage




class Limit(Filter):
     
     def __init__(
          self,
          seconds: float = 0,
          minutes: float = 0,
          hours: float = 0,
          days: float = 0,
          all_users: bool = False,
          storage: AbstractStorage | None = None,
          answer_callback: Callable[[Message, timedelta, datetime], Awaitable] | None = None
     ) -> None:
          if not isinstance(all_users, bool):
               raise TypeError("all_users must be bool type")
          
          if storage is not None:
               if not issubclass(type(storage), AbstractStorage):
                    raise TypeError(f"Invalid type for storage")
          
          if answer_callback is not None:
               if not inspect.iscoroutinefunction(answer_callback):
                    raise TypeError(f"answer_callback must be croutine function")
          
          # checks types
          self.storage = storage
          self.answer_callback = answer_callback
          self.all_users = all_users
          
          self.time = timedelta(
               seconds=seconds,
               minutes=minutes,
               hours=hours,
               days=days
          )
          
          
     async def __call__(self, message: Message, dispatcher: Dispatcher) -> bool:
          storage = dispatcher.workflow_data.get("storage", MemoryStorage())
          answer_callback = dispatcher.workflow_data.get("answer_callback")
          
          if self.storage is not None:
               storage = self.storage
               
          if self.answer_callback is not None:
               answer_callback = self.answer_callback
               
          user = str(message.from_user.id)
          if self.all_users is True:
               user = "users"
          
          user_time = await storage.get(user)
          if user_time is None:
               await storage.update(user, datetime.utcnow() + self.time)
               return True
               
          if user_time >= datetime.utcnow():
               time_last = user_time - datetime.utcnow()
               if answer_callback is not None:
                    await answer_callback(message, self.time, time_last)
               else:
                    await message.answer(f"Retry after {round(time_last.total_seconds(), 0)} seconds")
               return False
          
          await storage.update(user, datetime.utcnow() + self.time)
          return True
          