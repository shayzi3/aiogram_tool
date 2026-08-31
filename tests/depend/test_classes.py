from typing import Annotated

from aiogram.types import Message

from aiogram_tool.tools.depend import Depends

from .conftest import MiddlewareRegistryType, MyDispatcher


async def test_init_class(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    class InitMethod:
        def __init__(self) -> None:
            pass

    @my_dispatcher.message()
    async def handle(
        message: Message, ins: Annotated[InitMethod, Depends(InitMethod)]
    ) -> str:
        assert isinstance(message, Message)
        assert isinstance(ins, InitMethod)
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"


async def test_call_class(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    class CallMethod:
        def __init__(self, command: str) -> None:
            self.command = command

        async def __call__(self) -> str:
            return self.command

    @my_dispatcher.message()
    async def handle(
        message: Message, call: Annotated[str, Depends(CallMethod(command="command"))]
    ) -> str:
        assert isinstance(message, Message)
        assert call == "command"
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"
