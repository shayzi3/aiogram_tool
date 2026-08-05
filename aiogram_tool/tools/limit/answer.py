from datetime import timedelta

from aiogram.types import TelegramObject



class RateLimitAnswer:
          
     async def __call__(
          self, 
          event: TelegramObject, 
          window_time: timedelta, 
          retry_after: timedelta
     ) -> None:
          await event.answer(
               text=f"Next request after {retry_after.total_seconds()} seconds."
          )