from aiogram.types import Message

from aiogram_tool.tools.depend import Depends, DependTool

from .conftest import MiddlewareRegistryType, MyDispatcher


async def test_override_depends(
    my_dispatcher: MyDispatcher,
    middleware_register: MiddlewareRegistryType,
    depend_tool: DependTool,
) -> None:
    class TestDepend:
        def __init__(self):
            self.attr = "test"

    class TestDependOverride(TestDepend):
        def __init__(self):
            self.attr = "test_override"

    async def depend() -> int:
        return 10

    async def override_depend():
        return 3

    @my_dispatcher.message()
    async def handle(
        message: Message,
        integer: int = Depends(depend),
        test_depend: TestDepend = Depends(TestDepend),
    ) -> str:
        assert isinstance(message, Message)
        assert integer == 3
        assert test_depend.attr == "test_override"
        return "handle"

    depend_tool.dependency_override = {
        depend: Depends(override_depend),
        TestDepend: Depends(TestDependOverride),
    }

    middleware_register(["message"])
    handle_result = await my_dispatcher.message_update()

    assert handle_result == "handle"
