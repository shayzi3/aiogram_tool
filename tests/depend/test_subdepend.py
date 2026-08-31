from typing import Annotated

from aiogram.types import Message

from aiogram_tool.tools.depend import Depends

from .conftest import MiddlewareRegistryType, MyDispatcher


async def test_subdepend(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    class Test:
        def __init__(self, attr: str) -> None:
            self.attr = attr

    async def subdepend() -> Test:
        return Test(attr="Hello")

    async def depend(test: Annotated[Test, Depends(subdepend)]) -> Test:
        assert isinstance(test, Test)
        assert test.attr == "Hello"
        return Test(attr=test.attr + " Vlad!")

    @my_dispatcher.message()
    async def handle(message: Message, test: Annotated[Test, Depends(depend)]) -> str:
        assert isinstance(message, Message)
        assert isinstance(test, Test)
        assert test.attr == "Hello Vlad!"
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"
