import inspect

from datetime import datetime, timedelta

from aiogram import Dispatcher
from aiogram.filters import Filter
from aiogram.types.base import TelegramObject
from aiogram.dispatcher.event.handler import HandlerObject

from .utils.callback import AnswerCallback
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
          answer_callback: AnswerCallback | None = None
     ) -> None:
          if not isinstance(all_users, bool):
               raise TypeError("Invalid type for all_users")
          
          if storage is not None:
               if not issubclass(type(storage), AbstractStorage):
                    raise TypeError(f"Invalid type for storage")
          
          if answer_callback is not None:
               if not isinstance(answer_callback, AnswerCallback):
                    raise TypeError(f"Invalid type for answer_callback")
          
          self._storage = storage
          self._answer_callback = answer_callback
          self._all_users = all_users
          
          self._time = timedelta(
               seconds=seconds,
               minutes=minutes,
               hours=hours,
               days=days
          )
          
          
     async def __call__(
          self, 
          event: TelegramObject, 
          dispatcher: Dispatcher, 
          handler: HandlerObject
     ) -> bool:
          storage: AbstractStorage = dispatcher.get("storage", MemoryStorage())
          answer_callback: AnswerCallback | None = dispatcher.get("answer_callback", None)
          
          if self._storage is not None:
               storage = self._storage
               
          if self._answer_callback is not None:
               answer_callback = self._answer_callback
                    
          query = str(event.from_user.id) + "@" + handler.callback.__name__
          if self._all_users is True:
               query = "users" + "@" + handler.callback.__name__
          
          user_time = await storage.get(query)
          if user_time is None:
               await storage.update(query, datetime.utcnow() + self._time)
               return True
               
          if user_time >= datetime.utcnow():
               time_last = user_time - datetime.utcnow()
               if answer_callback is not None:
                    await answer_callback.call(event, self._time, time_last)
               else:
                    await event.answer(f"Retry after {round(time_last.total_seconds(), 0)} seconds")
               return False
          
          await storage.update(query, datetime.utcnow() + self._time)
          return True
          