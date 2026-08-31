from typing import Annotated

from aiogram.types import Message

from aiogram_tool.tools.depend import Depends

from .conftest import MiddlewareRegistryType, MyDispatcher


async def test_lambda_depend(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:

    @my_dispatcher.message()
    async def handle(
        message: Message, integer: Annotated[int, Depends(lambda: 1)]
    ) -> int:
        assert isinstance(message, Message)
        assert integer == 1
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"
