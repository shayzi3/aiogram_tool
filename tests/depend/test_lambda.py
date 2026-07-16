from typing import Annotated

from aiogram_tool.tools.depend.depend import Depends
from aiogram_tool.tools.depend.utils.resolver import DependResolver



async def handler_with_lambda(
     integer: Annotated[int, Depends(lambda num: num**2)]
) -> None:
     assert integer == 100
     

async def test_lambda_depend(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_with_lambda
     depend_resolver.middleware_data = {"num": 10}
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_with_lambda(**inject)
     