import secrets

from typing import Any, ClassVar
from typing_extensions import Self

from aiogram.filters.callback_data import CallbackQueryFilter, CallbackData
from aiogram.types import CallbackQuery
from magic_filter import MagicFilter

from aiogram_tool.tools.callback_data.answer import CallbackDataAnswer
from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.types import _MISSING
from .utils.pack_callback_data import pack_without_errors


UNIQUE_PREFIX: str = "UIDPR"


class _UniqueIDCallbackData(CallbackData, prefix=UNIQUE_PREFIX):
     unique_id: str
     callback_data_prefix: str
     
     @classmethod
     def build(cls, callback_data: CallbackData) -> Self:
          separators_len = len(cls.__separator__) * len(cls.model_fields)
          unique_id_len = (64 - (
               len(UNIQUE_PREFIX) + 
               len(callback_data.__prefix__) +
               separators_len
          )) // 2
          
          if unique_id_len < 6:
               raise ValueError(
                    f"Prefix '{callback_data.__prefix__}' at {callback_data.__class__.__name__} is too long. "
                    f"Unique id must be at least 6 bytes (12 chars)."
               )
               
          return cls(
               unique_id=secrets.token_hex(unique_id_len),
               callback_data_prefix=callback_data.__prefix__
          )

          
class LongCallbackQueryFilter(CallbackQueryFilter):
     
     async def __call__(self, query: CallbackQuery) -> bool | dict[str, Any]:
          if not isinstance(query, CallbackQuery) or not query.data:
               return False
          
          try:
               instance = _UniqueIDCallbackData.unpack(query.data)
          except (TypeError, ValueError):
               try:
                    instance = self.callback_data.unpack(query.data)
               except (TypeError, ValueError):
                    return False
          
          if isinstance(instance, _UniqueIDCallbackData):
               if instance.callback_data_prefix != getattr(self.callback_data, "__prefix__"):
                    return False
                    
               storage: BaseStorage = getattr(self.callback_data, "_storage")
               answer_callback: CallbackDataAnswer = getattr(self.callback_data, "_answer_callback")
               
               packed_callback_data = await storage.get_value(key=instance.unique_id)
               if packed_callback_data is _MISSING:
                    await answer_callback(query)
                    return False
               try:
                    instance = self.callback_data.unpack(packed_callback_data)
               except (TypeError, ValueError):
                    return False
               
          if self.rule is None or self.rule.resolve(instance):
               return {"callback_data": instance}
          return False
     
     
class LongCallbackData(CallbackData, prefix="?"):
     _storage: ClassVar[BaseStorage] = MemoryStorage()
     _answer_callback: ClassVar[CallbackDataAnswer] = CallbackDataAnswer()
     
     async def pack_long(self) -> str:
          try:
               return super().pack()
          except ValueError as ex:
               if "data is too long!" in str(ex):
                    callback_data_instance = _UniqueIDCallbackData.build(
                         callback_data=self
                    )
                    await self._storage.set_value(
                         key=callback_data_instance.unique_id,
                         value=pack_without_errors(self),
                    )    
                    return callback_data_instance.pack()
               raise ex
               
     @classmethod
     def filter(cls, rule: MagicFilter | None = None) -> LongCallbackQueryFilter:
          return LongCallbackQueryFilter(callback_data=cls, rule=rule)
               
               