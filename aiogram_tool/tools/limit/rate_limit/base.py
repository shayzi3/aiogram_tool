from abc import ABC, abstractmethod

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer


class BaseRateLimit(ABC):
     storage_prefix = "aiot_rate_limit"
     
     @abstractmethod
     def build_key(
          self,
          event: TelegramObject,
          unique_handler_name: str
     ) -> str:
          raise NotImplementedError
     
     @abstractmethod
     async def execute(
          self,
          event: TelegramObject,
          storage: BaseLockStorage,
          answer_callback: RateLimitAnswer,
          key: str
     ) -> bool:
          raise NotImplementedError