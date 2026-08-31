from typing import Annotated

import pytest
from aiogram.types import Message

from aiogram_tool.tools.depend.depend import Depends
from aiogram_tool.tools.depend.types.exceptions import (
    InvalidMiddlewareDataArgumentError,
)

from .conftest import MiddlewareRegistryType, MyDispatcher


async def test_arguments(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    async def depend(my_data: str, other_data: str) -> str:
        assert my_data == "hello" and other_data == "world"
        return my_data + "_" + other_data

    @my_dispatcher.message()
    async def handle(
        message: Message, depend_data: Annotated[str, Depends(depend)]
    ) -> None:
        assert isinstance(message, Message)
        assert depend_data == "hello_world"
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update(
        my_data="hello", other_data="world"
    )

    assert handle_result == "handle"


async def test_unknown_arguments(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    async def depend(argument: int) -> int:
        return argument

    @my_dispatcher.message()
    async def handle(
        message: Message, argument: Annotated[int, Depends(depend)]
    ) -> int:
        return argument

    middleware_register(["message"])
    with pytest.raises(InvalidMiddlewareDataArgumentError):
        await my_dispatcher.message_update()


async def test_default_argument(
    my_dispatcher: MyDispatcher, middleware_register: MiddlewareRegistryType
) -> None:
    async def depend(data: str = "name") -> str:
        return data

    @my_dispatcher.message()
    async def handle(
        message: Message, depend_data: Annotated[str, Depends(depend)]
    ) -> None:
        return depend_data + "_" + "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "name_handle"

    handle_result = await my_dispatcher.message_update(data="other")

    assert handle_result == "other_handle"
