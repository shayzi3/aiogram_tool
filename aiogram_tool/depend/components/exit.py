from aiogram.types.base import TelegramObject



class DependExit:
     def __init__(
          self, 
          event: TelegramObject | None = None,
          **event_kwargs
     ) -> None:
          if not hasattr(event, "answer") and event is not None:
               raise ValueError("event haven't method answer")
          
          self._event = event
          self._event_kwargs = event_kwargs
          
     async def event_answer(self) -> None:
          if self._event is not None:
               await self._event.answer(**self._event_kwargs)