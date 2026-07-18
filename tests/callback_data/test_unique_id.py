import pytest

from aiogram_tool.tools.callback_data.filter import LongCallbackData



async def test_unique_id_data_error() -> None:
     
     class Data(LongCallbackData, prefix="LONG"*13):
          attr: str
          
     with pytest.raises(ValueError):
          # Error is too long prefix
          await Data(attr="important_data").pack_long()
          
     