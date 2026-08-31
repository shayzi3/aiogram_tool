from abc import ABC, abstractmethod

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer


class BaseRateLimit(ABC):
    storage_prefix = "aiot_rate_limit"

    def build_key(
        self,
        event: TelegramObject,
        unique_handler_name: str,
        all_users: bool,
        key: str | None,
    ) -> str:
        if not getattr(event, "from_user", None):
            raise TypeError(
                f"Don't support event without attribute 'from_user'. Your event {event}"
            )
        user = "users" if all_users is True else str(event.from_user.id)
        last_part = key if key is not None else unique_handler_name

        return f"{self.storage_prefix}@{user}@{last_part}"

    @abstractmethod
    async def execute(
        self,
        event: TelegramObject,
        storage: BaseLockStorage,
        answer_callback: RateLimitAnswer,
        key: str,
    ) -> bool:
        raise NotImplementedError
