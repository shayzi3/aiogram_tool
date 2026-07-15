import pytest

from typing import Annotated

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.utils.resolver import DependResolver


async def handler_depend(
     my_data: str, 
     other_data: str
) -> str:
     assert my_data == "hello" and other_data == "world"
     return my_data + "_" + other_data


async def handler_with_default_params(
     my_data: str,
     other_data: str = "name"
) -> str:
     assert my_data == "hello" and other_data == "name"
     return my_data + "_" + other_data


async def handler(
     depend_data: Annotated[str, From(handler_depend)]
) -> None:
     return depend_data + "_" + "after_handler"


async def handler_with_default_params(
     depend_data: Annotated[str, From(handler_with_default_params)]
) -> None:
     return depend_data + "_" + "after_handler_with_default_params"


async def test_arguments(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler
     depend_resolver.middleware_data = {
          "my_data": "hello", 
          "other_data": "world"
     }
     inject = await depend_resolver.resolve_callback_depends()
     assert inject == {"depend_data": "hello_world"}
     
     handler_result = await handler(**inject)
     assert handler_result == "hello_world_after_handler"
     
  
async def test_unknown_arguments(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler
     
     with pytest.raises(ValueError):
          await depend_resolver.resolve_callback_depends()
          

async def test_default_argument(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_with_default_params
     depend_resolver.middleware_data = {"my_data": "hello"}
     
     inject = await depend_resolver.resolve_callback_depends()
     handler_result = await handler_with_default_params(**inject)
     assert handler_result == "hello_name_after_handler_with_default_params"
     
     