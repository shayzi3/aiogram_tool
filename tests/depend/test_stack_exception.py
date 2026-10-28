from contextlib import asynccontextmanager

import pytest

from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.utils.container_manager import ContainerManager


@pytest.mark.parametrize("scope", [Scope.REQUEST, Scope.TRANSIENT])
async def test_dependency_receives_handler_exception(scope):
    seen = []

    @asynccontextmanager
    async def dependency():
        try:
            yield
        except RuntimeError as exc:
            seen.append(exc)
            raise
        else:
            seen.append("success")

    error = RuntimeError("handler failed")
    container_manager = ContainerManager()
    with pytest.raises(RuntimeError) as caught:
        async with container_manager.transaction() as container_transaction:
            await container_transaction.stack_transaction.enter_async_context(
                dependency(), scope
            )
            raise error
    assert caught.value is error
    assert seen == [error]


async def test_dependency_receives_success():
    seen = []

    @asynccontextmanager
    async def dependency():
        yield
        seen.append("success")

    container_manager = ContainerManager()
    async with container_manager.transaction() as container_transaction:
        await container_transaction.stack_transaction.enter_async_context(
            dependency(), Scope.REQUEST
        )
    assert seen == ["success"]
