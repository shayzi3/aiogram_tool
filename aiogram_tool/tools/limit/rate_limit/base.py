from abc import ABC, abstractmethod
from asyncio import Lock

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.utils.answer.rate_limit import RateLimitAnswer
from aiogram_tool.tools.limit.tool import RateLimitTool


class BaseRateLimit(ABC):
     
     def build_key(
          self,
          event: TelegramObject,
          all_users: bool,
          unique_handler_name: str
     ) -> str:
          user = str(event.from_user.id) if not all_users else "users"
          return f"{user}@{unique_handler_name}"
     
     def get_lock(self, key: str, tool: RateLimitTool) -> Lock:
          if key not in tool.locks.keys():
               tool.locks[key] = Lock()
          return tool.locks[key]
     
     @abstractmethod
     async def execute(
          self,
          unique_handler_name: str,
          tool: RateLimitTool,
          event: TelegramObject,
          storage: BaseStorage,
          answer_callback: RateLimitAnswer
     ) -> bool:
          raise NotImplementedError