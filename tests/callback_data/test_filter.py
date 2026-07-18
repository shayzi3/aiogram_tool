import pytest

from aiogram import F
from aiogram.types import CallbackQuery

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.tools.callback_data.filter import (
     LongCallbackData, 
     LongCallbackQueryFilter,
     _UniqueIDCallbackData
)
from aiogram_tool.tools.callback_data.answer import CallbackDataAnswer
from .conftest import CallbackQueryFactoryType


@pytest.mark.parametrize(
     argnames=("data_kwargs"),
     argvalues=[
          (
               {
                    "name": "Vlad"*15,
                    "surname": "Dyadchenko",
                    "age": 18
               }
          ),
          (
               {
                    "name": "Aleksey",
                    "surname": "Lazarev",
                    "age": 18
               }
          )
     ]
)
async def test_filter(
     data_kwargs: dict,
     storage: BaseStorage,
     callback_query_factory: CallbackQueryFactoryType
) -> None:
     
     class Data(LongCallbackData, prefix="$"):
          _storage = storage
          
          name: str
          surname: str
          age: int
     
     callback_query_filter = LongCallbackQueryFilter(callback_data=Data)
     pack = await Data(**data_kwargs).pack_long()
     
     callback_query = callback_query_factory(pack)
     
     callback_data_after_filter = await callback_query_filter(callback_query)
     filter_instance = callback_data_after_filter["callback_data"]
     
     assert isinstance(filter_instance, Data)
     assert filter_instance.model_dump() == data_kwargs
     
     
async def test_answer_at_filter(
     storage: BaseStorage,
     callback_query_factory: CallbackQueryFactoryType
) -> None:
     
     class Answer(CallbackDataAnswer):
          
          def __init__(self) -> None:
               self.is_activate = False
               
          async def __call__(self, query: CallbackQuery) -> None:
               self.is_activate = True
     
     answer_callback = Answer()
          
     class Test(LongCallbackData, prefix="?"):
          _storage = storage
          _answer_callback = answer_callback
          
          attr: str
     
     callback_query_filter = LongCallbackQueryFilter(callback_data=Test)
     packed = _UniqueIDCallbackData.build(callback_data=Test).pack()
     
     callback_query = callback_query_factory(packed)
     
     assert await callback_query_filter(callback_query) is False
     assert answer_callback.is_activate
     
     
     
async def test_filter_false(
     storage: BaseStorage,
     callback_query_factory: CallbackQueryFactoryType
) -> None:
     
     class Test(LongCallbackData, prefix="*"):
          _storage = storage
          
          attr: str
          
     class Data(LongCallbackData, prefix="*"):
          _storage = storage
          
          attr_one: str
          attr_two: str
          
     class TestTwo(LongCallbackData, prefix="!"):
          _storage = storage
          
          some_attr: str
          
     callback_query_filter = LongCallbackQueryFilter(callback_data=Test)
     
     callback_query = callback_query_factory(None)
     assert await callback_query_filter(callback_query) is False
     assert await callback_query_filter(None) is False
     
     callback_query = callback_query_factory("my_some_data")
     assert await callback_query_filter(callback_query) is False
     
     packed = await TestTwo(some_attr="data"*30).pack_long()
     callback_query = callback_query_factory(packed)
     assert await callback_query_filter(callback_query) is False
     
     packed = await Data(attr_one="STRING"*10, attr_two="Two").pack_long()
     callback_query = callback_query_factory(packed)
     assert await callback_query_filter(callback_query) is False
     
     callback_query_filter = LongCallbackQueryFilter(
          callback_data=Test,
          rule=F.attr.contains("Hello")
     )
     packed = await Test(attr="my_attr").pack_long()
     callback_query = callback_query_factory(packed)
     assert await callback_query_filter(callback_query) is False
          
     