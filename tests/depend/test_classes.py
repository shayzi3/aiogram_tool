from typing import Annotated

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.utils.resolver import DependResolver



class InitMethod:
     
     def __init__(self, argument: str):
          self.argument = argument
          
     def hello(self) -> str:
          return "Hello" + "_" + self.argument
     

class CallMethod:
     
     def __init__(self, command: str) -> None:
          self.command = command
     
     async def __call__(self, name: str) -> str:
          return self.command + "-" + name
     
     
async def handler_with_init_depend(
     my_init: Annotated[InitMethod, From(InitMethod)]
) -> str:
     assert isinstance(my_init, InitMethod)
     return my_init.hello()


async def handler_with_call_depend(
     my_call: Annotated[str, From(CallMethod(command="Hello"))]
) -> str:
     assert my_call == "Hello-Vlad"
     return my_call + "_" + "after_handler_with_call_depend"


async def test_init_class(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_with_init_depend
     depend_resolver.middleware_data = {"argument": "Vlad"}
     
     inject = await depend_resolver.resolve_callback_depends()
     handler_result = await handler_with_init_depend(**inject)
     assert handler_result == "Hello_Vlad"
     
async def test_call_class(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_with_call_depend
     depend_resolver.middleware_data = {"name": "Vlad"}
     
     inject = await depend_resolver.resolve_callback_depends()
     handler_result = await handler_with_call_depend(**inject)
     assert handler_result == "Hello-Vlad_after_handler_with_call_depend"