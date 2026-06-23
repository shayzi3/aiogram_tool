from datetime import timedelta, datetime

from aiogram.types import TelegramObject

from .base import BaseAnswer



class RateLimitAnswer(BaseAnswer):
          
     async def __call__(
          self, 
          event: TelegramObject, 
          time: timedelta, 
          lost_time: datetime
     ) -> None:
          ...