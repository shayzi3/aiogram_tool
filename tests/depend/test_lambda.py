from typing import Annotated

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.utils.resolver import DependResolver


NUMBER = 15


async def handler_with_lambda(
     integer: Annotated[int, From(lambda num: num**2)]
) -> None:
     assert integer == NUMBER**2
     

async def test_lambda_depend(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_with_lambda
     depend_resolver.middleware_data = {"num": NUMBER}
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_with_lambda(**inject)
     