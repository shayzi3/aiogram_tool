import pytest
import secrets

from typing import Any
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.types import Update, Message, Chat, User

from aiogram_tool.tools.limit import RateLimitTool



class MyDispatcher(Dispatcher):
     
     async def message_update(self, user_id: int) -> Any:
          return await self.feed_update(
               bot=Bot(token="123:MeowMeow"),
               update=Update(
                    update_id=123,
                    message=Message(
                         message_id=123,
                         date=datetime.now(),
                         chat=Chat(id=123, type="private"),
                         from_user=User(
                              id=user_id,
                              is_bot=False,
                              first_name="Vlad"
                         )
                    ),
               ),
               dispatcher=self
          )


@pytest.fixture(scope="function")
def my_dispatcher() -> MyDispatcher:
     return MyDispatcher()

@pytest.fixture(scope="function")
def rate_limit_tool() -> RateLimitTool:
     return RateLimitTool()