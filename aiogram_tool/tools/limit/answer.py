from datetime import timedelta, datetime

from aiogram.types import TelegramObject



class RateLimitAnswer:
          
     async def __call__(
          self, 
          event: TelegramObject, 
          time: timedelta, 
          lost_time: datetime
     ) -> None:
          ...