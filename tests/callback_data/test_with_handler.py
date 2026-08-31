from typing import Any

import pytest
from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import CallbackQuery, Update

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.callback_data.answer import CallbackDataAnswer
from aiogram_tool.tools.callback_data.filter import (
    LongCallbackData,
    _UniqueIDCallbackData,
)

from .conftest import CallbackQueryFactoryType


class MyDispatcher(Dispatcher):
    async def callback_query_update(self, callback_query: CallbackQuery) -> Any:
        return await self.feed_update(
            bot=Bot(token="123:MeowMeow"),
            update=Update(update_id=123, callback_query=callback_query),
        )


@pytest.fixture(scope="function")
def my_dispatcher() -> MyDispatcher:
    return MyDispatcher()


async def test_filter_with_handler(
    my_dispatcher: MyDispatcher,
    callback_query_factory: CallbackQueryFactoryType,
    storage: BaseStorage,
):
    class MyAnswer(CallbackDataAnswer):
        def __init__(self) -> None:
            self.is_pushed = False

        async def __call__(self, query: CallbackQuery) -> None:
            assert isinstance(query, CallbackQuery)
            self.is_pushed = True

    my_answer = MyAnswer()

    class MyCallbackData(LongCallbackData, prefix="*"):
        _storage = storage
        _answer_callback = my_answer

        name: str
        surname: str
        age: int

    @my_dispatcher.callback_query(MyCallbackData.filter(F.age >= 18))
    async def handle(query: CallbackQuery, callback_data: MyCallbackData) -> None:
        assert isinstance(query, CallbackQuery)
        assert isinstance(callback_data, MyCallbackData)
        return "handle"

    packed_short = await MyCallbackData(
        name="Vlad", surname="Dyadchenko", age=19
    ).pack_long()

    packed_long = await MyCallbackData(
        name="Vlad" * 15, surname="Dyadchenko", age=19
    ).pack_long()

    unhandled_packed = await MyCallbackData(
        name="Vlad" * 15, surname="Dyadchenko", age=10
    ).pack_long()

    long_data_without_save = _UniqueIDCallbackData.build(
        callback_data=MyCallbackData
    ).pack()

    results = [
        await my_dispatcher.callback_query_update(callback_query_factory(query))
        for query in [
            packed_short,
            packed_long,
            unhandled_packed,
            long_data_without_save,
        ]
    ]
    assert results == ["handle", "handle", UNHANDLED, UNHANDLED]
    assert my_answer.is_pushed is True
