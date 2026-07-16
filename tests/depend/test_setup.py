import pytest

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from aiogram_tool.tools.depend import (
     DependTool,
     ScopeRegistry,
     Depends
)
from aiogram_tool.tools.depend.types.exceptions import DependencyOverrideError, ObserverError
from aiogram_tool.tools.depend.components.inner_middleware import DependInnerMiddleware
from aiogram_tool.tools.depend.utils.registry_manager import DependRegistryTransactionManager
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransactionManager



def test_depend_tool(
     depend_tool: DependTool,
     dispatcher: Dispatcher
) -> None:
     
     @dispatcher.message()
     async def test_handler(message: Message):
          ...
          
     @dispatcher.callback_query()
     async def test_query_handler(query: CallbackQuery):
          ...
     
     assert isinstance(depend_tool.dependency_override, dict)
     assert (
          isinstance(depend_tool.allowed_updates, list) or 
          depend_tool.allowed_updates is None
     )
     assert isinstance(depend_tool.scope_registry, ScopeRegistry)
     assert isinstance(depend_tool.registry, DependRegistryTransactionManager)
     assert isinstance(depend_tool.stack_manager, AsyncExitStackTransactionManager)
     
     depend_tool.setup(dispatcher=dispatcher)
     
     shutdown_events = dispatcher.shutdown.handlers
     assert shutdown_events[1].callback == depend_tool.shutdown
     
     for event in dispatcher.resolve_used_update_types():
          oberver = dispatcher.observers.get(event)
          middlewares = getattr(oberver.middleware, "_middlewares")
          assert isinstance(middlewares[0], DependInnerMiddleware)
          
     
def test_depend_tool_errors() -> None:
     def some() -> None:
          return
     
     with pytest.raises(DependencyOverrideError):
          DependTool(
               dependency_override={some: 1}
          )
          DependTool(
               dependency_override={1: Depends(some)}
          )
          
          
def test_depend_tool_allowed_updates_error(
     dispatcher: Dispatcher,
     depend_tool: DependTool
) -> None:
     depend_tool.allowed_updates = ["message", "other"]
     with pytest.raises(ObserverError):
          depend_tool.setup(dispatcher=dispatcher)
          
          
def test_depend_tool_allowed_updates_empty(
     dispatcher: Dispatcher,
     depend_tool: DependTool
) -> None:
     
     @dispatcher.message()
     async def test_handler(message: Message):
          ...
          
     @dispatcher.callback_query()
     async def test_query_handler(query: CallbackQuery):
          ...
     
     depend_tool.allowed_updates = []
     depend_tool.setup(dispatcher=dispatcher)
     
     for event in dispatcher.resolve_used_update_types():
          oberver = dispatcher.observers.get(event)
          assert not getattr(oberver.middleware, "_middlewares")
          
          
def test_depend_tool_allowed_updates(
     dispatcher: Dispatcher,
     depend_tool: DependTool
) -> None:
     
     @dispatcher.message()
     async def test_handler(message: Message):
          ...
          
     @dispatcher.callback_query()
     async def test_query_handler(query: CallbackQuery):
          ...
     
     depend_tool.allowed_updates = ["message"]
     depend_tool.setup(dispatcher=dispatcher)
     
     for event in dispatcher.resolve_used_update_types():
          oberver = dispatcher.observers.get(event)
          if oberver.event_name == "message":
               assert isinstance(
                    getattr(oberver.middleware, "_middlewares")[0],
                    DependInnerMiddleware
               )
               
          elif oberver.event_name == "callback_query":
               assert not getattr(oberver.middleware, "_middlewares")


     
     
     