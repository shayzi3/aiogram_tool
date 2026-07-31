import asyncio

from aiogram.types import Message

from aiogram_tool.tools.depend import ScopeRegistry, Scope, Depends, DependTool

from .conftest import MyDispatcher, MiddlewareRegistryType


async def test_singleton_lock(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     my_dispatcher: MyDispatcher,
     middleware_register: MiddlewareRegistryType
) -> None:
     depend_tool.scope_registry = scope_registry
     
     class Test:
          ...
          
     @scope_registry(Scope.SINGLETON)
     async def depend(
          wait_time: int, 
          flag: bool, 
     ) -> Test:
          await asyncio.sleep(wait_time)
          assert flag is True
          return Test()
          
     @my_dispatcher.message()
     async def handle(message: Message, test: Test = Depends(depend)) -> None:
          assert isinstance(message, Message)
          assert isinstance(test, Test)
          return "handle"
          
     middleware_data = (
          {"wait_time": 0.2, "flag": True},
          {"wait_time": 0.01, "flag": False}
     )
     middleware_register(["message"])
     result = await asyncio.gather(
          *[
               my_dispatcher.message_update(**middleware_data[0]),
               my_dispatcher.message_update(**middleware_data[1])
          ]
     )
     assert result == ["handle", "handle"]