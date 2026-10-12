from contextlib import AsyncExitStack, asynccontextmanager

import pytest

from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction


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
    async with AsyncExitStack() as app_stack:
        with pytest.raises(RuntimeError) as caught:
            async with AsyncExitStackTransaction(app_stack) as transaction:
                await transaction.enter_async_context(dependency(), scope)
                raise error
    assert caught.value is error
    assert seen == [error]


async def test_dependency_receives_success():
    seen = []

    @asynccontextmanager
    async def dependency():
        yield
        seen.append("success")

    async with AsyncExitStack() as app_stack:
        async with AsyncExitStackTransaction(app_stack) as transaction:
            await transaction.enter_async_context(dependency(), Scope.REQUEST)
    assert seen == ["success"]
