import pytest

from aiogram_tool.storage.impl.memory import MemoryStorage
from aiogram_tool.tools.callback_data.filter import (
    LongCallbackData,
    LongCallbackQueryFilter,
    _UniqueIDCallbackData,
)

from .conftest import CallbackQueryFactoryType


async def test_unique_id_data_error() -> None:

    class Data(LongCallbackData, prefix="LONG" * 13):
        attr: str

    with pytest.raises(ValueError):
        # Error is too long prefix
        await Data(attr="important_data").pack_long()


async def test_unicode_prefix_unique_id_respects_telegram_byte_limit(
    callback_query_factory: CallbackQueryFactoryType,
) -> None:
    class Data(LongCallbackData, prefix="🐍" * 10):
        _storage = MemoryStorage()

        attr: str

    unique_id = _UniqueIDCallbackData.build(Data).pack()
    assert len(unique_id.encode("utf-8")) <= 64

    packed = await Data(attr="important_data" * 10).pack_long()
    assert len(packed.encode("utf-8")) <= 64

    result = await LongCallbackQueryFilter(callback_data=Data)(
        callback_query_factory(packed)
    )
    assert result["callback_data"] == Data(attr="important_data" * 10)
