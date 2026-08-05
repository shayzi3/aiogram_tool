import pytest
import secrets

from typing import Callable

from aiogram.types import CallbackQuery, User


CallbackQueryFactoryType = Callable[[str | None], CallbackQuery]
      

@pytest.fixture(scope="session")
def callback_query_factory() -> CallbackQueryFactoryType:
     def factory(callback_data: str | None) -> CallbackQuery:
          return CallbackQuery(
               id=str(secrets.randbits(k=10)),
               chat_instance="instance",
               data=callback_data,
               from_user=User(
                    id=secrets.randbits(k=10),
                    is_bot=False,
                    first_name="Vlad"
               )
          )
     return factory
          
     