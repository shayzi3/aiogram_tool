from aiogram_tool.tools.callback_data.filter import (
     LongCallbackData, 
     _UniqueIDCallbackData,
     LongCallbackQueryFilter
)
from aiogram_tool.storage.base import BaseStorage


async def test_pack(
     storage: BaseStorage
) -> None:
     class HeavyCallbackData(LongCallbackData, prefix="*"):
          _storage = storage
          
          attr_one: str
          attr_two: str
          
     ins_default = HeavyCallbackData(
          attr_one="Hello",
          attr_two="Vlad"
     )
     default_pack = await ins_default.pack_long()
     HeavyCallbackData.unpack(default_pack)
     
     heavy_ins = HeavyCallbackData(
          attr_one="Hello"*15,
          attr_two="Vlad"*15
     )
     heavy_pack = await heavy_ins.pack_long()
     
     unique_id = _UniqueIDCallbackData.unpack(heavy_pack)
     value_from_storage = await storage.get_value(
          key=unique_id.get_storage_key()
     )
     HeavyCallbackData.unpack(value_from_storage)
     
     assert isinstance(HeavyCallbackData.filter(), LongCallbackQueryFilter)
     
     
     