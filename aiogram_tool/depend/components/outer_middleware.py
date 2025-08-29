from typing import Any, Callable, Awaitable
from contextlib import AsyncExitStack

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types.base import TelegramObject



class StackMiddleware(BaseMiddleware):
     
     async def __call__(
          self, 
          handler: Callable[[TelegramObject, dict[str, Any]], Awaitable],
          event: TelegramObject, 
          data: dict[str, Any]
     ):
          async with AsyncExitStack() as stack:
               data.update({"async_stack": stack})
               return await handler(event, data)