from typing import Any

from aiogram.types import CallbackQuery

from .base import BaseAnswer



class CallbackDataAnswer(BaseAnswer):
          
     async def __call__(self, query: CallbackQuery) -> Any:
          ...