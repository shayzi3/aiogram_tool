from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, Self

import pytest
from aiogram import F
from aiogram.types import Message

from aiogram_tool.tools.depend.depend import Depends
from aiogram_tool.tools.depend.types.exceptions import ContextManagerError

from .conftest import MiddlewareRegistryType, MyDispatcher


class Session:
    def __init__(self):
        self.flag = None

    async def __aenter__(self) -> Self:
        self.flag = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.flag = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


class SessionManager:
    def __init__(self) -> None:
        self.ctx = Session()
        self.gen = Session()

    @asynccontextmanager
    async def async_context(self):
        async with self.ctx as session:
            yield session

    async def async_generator(self):
        async with self.gen as session:
            yield session

    @contextmanager
    def sync_context(self):
        with self.ctx as session:
            yield session

    def sync_generator(self):
        with self.gen as session:
            yield session


@pytest.fixture(scope="function")
def sessions() -> SessionManager:
    return SessionManager()


async def test_handler_async(
    my_dispatcher: MyDispatcher,
    middleware_register: MiddlewareRegistryType,
    sessions: SessionManager,
) -> None:
    @my_dispatcher.message()
    async def handle_async(
        message: Message,
        async_ctx: Annotated[Session, Depends(sessions.async_context)],
        async_gen: Annotated[Session, Depends(sessions.async_generator)],
    ):
        assert isinstance(message, Message)
        assert async_ctx.flag is True
        assert async_gen.flag is True
        return "handle"

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"
    assert sessions.ctx.flag is False
    assert sessions.gen.flag is False


async def test_handler_sync(
    my_dispatcher: MyDispatcher,
    middleware_register: MiddlewareRegistryType,
    sessions: SessionManager,
) -> None:

    @my_dispatcher.message(F.text == "sync_ctx")
    async def handle_sync_ctx(
        message: Message,
        sync_ctx: Annotated[Session, Depends(sessions.sync_context)],
    ): ...

    @my_dispatcher.message(F.text == "sync_gen")
    async def handle_sync_gen(
        message: Message, sync_gen: Annotated[Session, Depends(sessions.sync_generator)]
    ): ...

    middleware_register(["message"])
    with pytest.raises(ContextManagerError):
        await my_dispatcher.message_update(text="sync_ctx")

    with pytest.raises(ContextManagerError):
        await my_dispatcher.message_update(text="sync_gen")
