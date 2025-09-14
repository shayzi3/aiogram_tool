from typing import Any
from string import digits, ascii_letters
from random import choice

from aiogram.filters.callback_data import CallbackQueryFilter, CallbackData
from aiogram.types import CallbackQuery
from magic_filter import MagicFilter

from .storage import data_storage



class UniqueIDCallbackData(CallbackData, prefix="?"):
     mode: str = "__unique_id_callback"
     unique_id: str
     


class LongCallbackQueryFilter(CallbackQueryFilter):
     
     async def __call__(
          self, 
          query: CallbackQuery, 
     ) -> bool | dict[str, Any]:
          if not isinstance(query, CallbackQuery) or not query.data:
               return False
          try:
               callback_data_model = (
                    UniqueIDCallbackData
                    if "__unique_id_callback" in query.data
                    else self.callback_data
               )
               callback_data = callback_data_model.unpack(query.data)
          except (TypeError, ValueError):
               return False
          
          if isinstance(callback_data, UniqueIDCallbackData):
               callback_data = data_storage.get_value(key=callback_data.unique_id)
               if callback_data is None:
                    await query.answer("Button expired")
                    return False
               
          if self.rule is None or self.rule.resolve(callback_data):
               return {"callback_data": callback_data}
          return False
     
     
class LongCallbackData(CallbackData, prefix="?"):
     
     def pack(self) -> str:
          try:
               return super().pack()
          except ValueError as ex:
               if "long" in str(ex):
                    unique_id = self.__generate_unique_id()
                    data_storage.set_value(key=unique_id, value=self)
                    return UniqueIDCallbackData(unique_id=unique_id).pack()
               raise ex
               
     @classmethod
     def filter(cls, rule: MagicFilter | None = None) -> LongCallbackQueryFilter:
          return LongCallbackQueryFilter(callback_data=cls, rule=rule)
               
               
     def __generate_unique_id(self) -> str:
          symbols = ascii_letters + digits
          return "".join([choice(symbols) for _ in range(35)])  