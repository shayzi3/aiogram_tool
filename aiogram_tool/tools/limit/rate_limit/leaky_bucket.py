from datetime import timedelta, datetime, timezone

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseStorage
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.tools.limit.tool import RateLimitTool
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from .base import BaseRateLimit


class LeakyBucketRateLimit(BaseRateLimit):
     ...