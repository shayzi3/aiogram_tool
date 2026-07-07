from abc import ABC, abstractmethod

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer
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
     
     @abstractmethod
     async def execute(
          self,
          unique_handler_name: str,
          tool: RateLimitTool,
          event: TelegramObject,
          storage: BaseLockStorage,
          answer_callback: RateLimitAnswer
     ) -> bool:
          raise NotImplementedError