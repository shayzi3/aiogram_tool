import asyncio
import secrets

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram_tool.tools.depend import (
     DependTool,
     Depends,
     ScopeRegistry,
     Scope,
)
from aiogram_tool.tools.setup import aiogram_tool_setup


bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()

# Custom scope registry
scope_registry = ScopeRegistry()


# SINGLETON scope: initialized once per app lifecycle
@scope_registry(Scope.SINGLETON)
async def get_app_config() -> str:
     print("Initializing App Config...")
     return "APP_CONFIG_V1"


# REQUEST scope: initialized per update/request
@scope_registry(Scope.REQUEST)
async def get_request_id() -> int:
     return secrets.randbits(20)


# TRANSIENT scope: initialized every time it's called
@scope_registry(Scope.TRANSIENT)
async def get_message(req_id: str = Depends(get_request_id)) -> str:
     if req_id % 2 != 0:
          return "Odd seconds"
     return "Even seconds"


@dp.message(CommandStart())
async def start_handler(
    message: Message,
    config: str = Depends(get_app_config),
    req_id: int = Depends(get_request_id),
    request_id_message: str = Depends(get_message),
):
     await message.answer(f"Config {config}. {req_id} {request_id_message}")


async def main():
     depend_tool = DependTool(scope_registry=scope_registry)
     aiogram_tool_setup(dp, [depend_tool])
     
     await dp.start_polling(bot)


if __name__ == "__main__":
     asyncio.run(main())