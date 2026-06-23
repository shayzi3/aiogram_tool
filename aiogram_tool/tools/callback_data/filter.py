import secrets

from typing import Any, Union, Dict, Optional, ClassVar

from aiogram.filters.callback_data import CallbackQueryFilter, CallbackData
from aiogram.types import CallbackQuery
from magic_filter import MagicFilter

from aiogram_tool.utils.async_manager import async_manager
from .utils.pack_callback_data import pack_without_errors
from .config import CallbackDataConfig



UNIQUE_ID_PREFIX: str = "UIDPR"


class _UniqueIDCallbackData(CallbackData, prefix=UNIQUE_ID_PREFIX):
     unique_id: str
     
     
class LongCallbackQueryFilter(CallbackQueryFilter):
     
     async def __call__(self, query: CallbackQuery) -> Union[bool, Dict[str, Any]]:
          if not isinstance(query, CallbackQuery) or not query.data:
               return False
          
          try:
               callback_data_instance = (
                    _UniqueIDCallbackData
                    if query.data[:len(UNIQUE_ID_PREFIX)] == UNIQUE_ID_PREFIX
                    else self.callback_data
               ).unpack(query.data)
          except (TypeError, ValueError):
               return False
          
          if isinstance(callback_data_instance, _UniqueIDCallbackData):
               callback_data_config: CallbackDataConfig = getattr(self.callback_data, "_callback_data_config")
               
               packed_callback_data = await callback_data_config.storage.get_value(
                    key=callback_data_instance.unique_id,
                    prefix=callback_data_config.tool
               )
               if packed_callback_data is None:
                    await callback_data_config.answer.call(query)
               try:
                    callback_data_instance = self.callback_data.unpack(packed_callback_data)
               except (TypeError, ValueError):
                    return False
          
          if self.rule is None or self.rule.resolve(callback_data_instance):
               return {"callback_data": callback_data_instance}
          return False
     
     
class LongCallbackData(CallbackData, prefix="?"):
     _callback_data_config: ClassVar[CallbackDataConfig]
     
     def pack(self) -> str:
          try:
               return super().pack()
          except ValueError as ex:
               if "data is too long!" in str(ex):
                    if hasattr(self, "_callback_data_config") is False:
                         raise ValueError(f"Not found CallbackDataTool")
                    
                    unique_id = secrets.token_hex(25)
                    with async_manager as manager:
                         manager.run_coroutine(
                              self._callback_data_config.storage.set_value(
                                   key=unique_id,
                                   value=pack_without_errors(self),
                                   prefix=self._callback_data_config.tool
                              )    
                         )
                    return _UniqueIDCallbackData(unique_id=unique_id).pack()
               raise ex
               
     @classmethod
     def filter(cls, rule: Optional[MagicFilter] = None) -> LongCallbackQueryFilter:
          return LongCallbackQueryFilter(callback_data=cls, rule=rule)
               
               