from aiogram_tool.storage import MemoryLockStorage
from aiogram_tool.tools.limit import RateLimitAnswer, RateLimitTool

from .conftest import MyDispatcher


async def test_setup(
    my_dispatcher: MyDispatcher, rate_limit_tool: RateLimitTool
) -> None:
    rate_limit_tool.setup(my_dispatcher)

    assert isinstance(rate_limit_tool.answer_callback, RateLimitAnswer)
    assert isinstance(rate_limit_tool.storage, MemoryLockStorage)
    assert isinstance(my_dispatcher.workflow_data["rate_limit"], RateLimitTool)
