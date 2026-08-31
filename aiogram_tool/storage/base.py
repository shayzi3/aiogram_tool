from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from aiogram_tool.types import _MISSING


class BaseStorage(ABC):
    @abstractmethod
    async def set_value(self, key: str, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_value(self, key: str) -> str | _MISSING:
        raise NotImplementedError


class BaseLockStorage(BaseStorage):
    @abstractmethod
    async def lock(self, key: str) -> AbstractAsyncContextManager[None]:
        raise NotImplementedError
