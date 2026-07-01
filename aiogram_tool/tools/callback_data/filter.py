import secrets

from typing import Any, Union, Dict, Optional, ClassVar
from typing_extensions import Self

from aiogram.filters.callback_data import CallbackQueryFilter, CallbackData
from aiogram.types import CallbackQuery
from magic_filter import MagicFilter

from aiogram_tool.utils.answer.callback_data import CallbackDataAnswer
from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.utils.async_manager import async_manager
from .utils.pack_callback_data import pack_without_errors


UNIQUE_PREFIX: str = "UIDPR"
SEPARATOR: str = "-"


class _UniqueIDCallbackData(CallbackData, prefix=UNIQUE_PREFIX):
     unique_id: str
     
     @classmethod
     def build_unique_id(cls, callback_data_prefix: str) -> Self:
          secret = secrets.randbits(
               k=64 - (len(callback_data_prefix) + len(UNIQUE_PREFIX) + 2)
          )
          return cls(unique_id=SEPARATOR.join([callback_data_prefix, str(secret)]))
     
     def get_prefix_and_secret(self) -> list[str, str]:
          return self.unique_id.split(SEPARATOR)
     
     
class LongCallbackQueryFilter(CallbackQueryFilter):
     
     async def __call__(self, query: CallbackQuery) -> Union[bool, Dict[str, Any]]:
          if not isinstance(query, CallbackQuery) or not query.data:
               return False
          
          try:
               callback_data_instance = (
                    _UniqueIDCallbackData
                    if query.data[:len(UNIQUE_PREFIX)] == UNIQUE_PREFIX
                    else self.callback_data
               ).unpack(query.data)
          except (TypeError, ValueError):
               return False
          
          if isinstance(callback_data_instance, _UniqueIDCallbackData):
               prefix, unique_id = callback_data_instance.get_prefix_and_secret()
               if prefix != self.callback_data.__prefix__:
                    return False
                    
               storage: BaseStorage = getattr(self.callback_data, "_storage")
               answer_callback: CallbackDataAnswer = getattr(self.callback_data, "_answer_callback")
               
               packed_callback_data = await storage.get_value(
                    key=unique_id,
               )
               if packed_callback_data is None:
                    await answer_callback(query)
                    return False
               try:
                    callback_data_instance = self.callback_data.unpack(packed_callback_data)
               except (TypeError, ValueError):
                    return False
               
          if self.rule is None or self.rule.resolve(callback_data_instance):
               return {"callback_data": callback_data_instance}
          return False
     
     
class LongCallbackData(CallbackData, prefix="?"):
     _storage: ClassVar[BaseStorage] = MemoryStorage()
     _answer_callback: ClassVar[CallbackDataAnswer] = CallbackDataAnswer()
     
     def pack(self) -> str:
          try:
               return super().pack()
          except ValueError as ex:
               if "data is too long!" in str(ex):
                    unique_id_data = _UniqueIDCallbackData.build_unique_id(
                         callback_data_prefix=self.__prefix__
                    )
                    _, unique_id = unique_id_data.get_prefix_and_secret()
                    with async_manager as manager:
                         manager.run_coroutine(
                              self._storage.set_value(
                                   key=unique_id,
                                   value=pack_without_errors(self),
                              )    
                         )
                    return unique_id_data.pack()
               raise ex
               
     @classmethod
     def filter(cls, rule: Optional[MagicFilter] = None) -> LongCallbackQueryFilter:
          return LongCallbackQueryFilter(callback_data=cls, rule=rule)
               
               