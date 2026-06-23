from aiogram.types.base import TelegramObject



class DependExit:
     __slots__ = ("__event", "__event_kwargs",)
     
     def __init__(
          self, 
          event: TelegramObject | None = None,
          **event_kwargs
     ) -> None:
          if not hasattr(event, "answer") and event is not None:
               raise ValueError("event haven't method answer")
          
          self.__event = event
          self.__event_kwargs = event_kwargs
          
     async def event_answer(self) -> None:
          if self.__event is not None:
               await self.__event.answer(**self.__event_kwargs)