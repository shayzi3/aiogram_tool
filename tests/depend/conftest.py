import pytest

from typing import Any, Callable
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.types import Message, Update, Chat

from aiogram_tool.tools.depend.tool import DependTool
from aiogram_tool.tools.depend.utils.scope_registry import ScopeRegistry
from aiogram_tool.tools.depend.components.inner_middleware import DependInnerMiddleware
from aiogram_tool.tools.depend.components.outer_middleware import DependOuterMiddleware


MiddlewareRegistryType = Callable[[list[str]], None]

class MyDispatcher(Dispatcher):
     
     def middleware_register(
          self, 
          depend_tool: DependTool, 
          observers: list[str]
     ) -> None:
          for observer in observers:
               ins_observer = self.observers.get(observer)
               ins_observer.outer_middleware(DependOuterMiddleware(depend_tool))
               ins_observer.middleware(DependInnerMiddleware(depend_tool))
     
     async def message_update(
          self, 
          text: str | None = None,
          **middleware_data
     ) -> Any:
          return await self.feed_update(
               bot=Bot(token="123:MeowMeow"),
               update=Update(
                    update_id=123,
                    message=Message(
                         message_id=123,
                         date=datetime.now(),
                         chat=Chat(id=123, type="private"),
                         text=text
                    )
               ),
               **middleware_data
          )

@pytest.fixture(scope="function")
def depend_tool() -> DependTool:
     return DependTool()

@pytest.fixture(scope="function")
def my_dispatcher() -> MyDispatcher:
     return MyDispatcher()

@pytest.fixture(scope="function")
def middleware_register(
     my_dispatcher: MyDispatcher,
     depend_tool: DependTool
) -> MiddlewareRegistryType:
     def register(observers: list[str]) -> None:
          my_dispatcher.middleware_register(depend_tool, observers)
     return register
          
@pytest.fixture(scope="function")
def scope_registry() -> ScopeRegistry:
     return ScopeRegistry()