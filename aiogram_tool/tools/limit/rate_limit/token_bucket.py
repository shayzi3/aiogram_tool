from datetime import UTC, datetime, timedelta

from aiogram.types import TelegramObject

from aiogram_tool.storage.base import BaseLockStorage
from aiogram_tool.tools.limit.answer import RateLimitAnswer
from aiogram_tool.tools.limit.schema import UserLimit
from aiogram_tool.types import _MISSING

from .base import BaseRateLimit


class TokenBucketRateLimit(BaseRateLimit):
    storage_prefix = "token_bucket_aiot_rate_limit"

    def __init__(
        self,
        bucket_size: int,
        current_tokens: int = 1,
        refill_time: timedelta = timedelta(seconds=1),
        refill_tokens: int = 1,
    ) -> None:
        """Tocken bucket

        Args:
            bucket_size (int): maximum replenishable number of tokens
            current_tokens (int, optional): initial number of tokens. Defaults to 1.
            refill_time (timedelta, optional): time it takes for refill tokens to arrive. Defaults to timedelta(seconds=1).
            refill_tokens (int, optional): number of tokens received during the refill time. Defaults to 1.
        """
        if not all(
            [value > 0 for value in [bucket_size, current_tokens, refill_tokens]]
        ):
            raise ValueError(
                "args bucket_size, current_tokens, refill_tokens must be greater than 0"
            )

        self.bucket_size = bucket_size
        self.current_tokens = current_tokens
        self.refill_rate = refill_tokens / refill_time.total_seconds()
        self.time_before_request = timedelta(seconds=1 / self.refill_rate)

    @staticmethod
    def count_new_tokens(
        current_tokens: float,
        current_time: datetime,
        last_time: datetime,
        refill_rate: float,
        bucket_size: int,
    ) -> float:
        past_tense = (current_time - last_time).total_seconds()
        new_tokens = past_tense * refill_rate
        return min(bucket_size, current_tokens + new_tokens)

    async def execute(
        self,
        event: TelegramObject,
        storage: BaseLockStorage,
        answer_callback: RateLimitAnswer,
        key: str,
    ) -> bool:
        lock = await storage.lock(key)
        async with lock:
            current_time = datetime.now(tz=UTC)

            bucket = await storage.get_value(key=key)
            if bucket is _MISSING:
                await storage.set_value(
                    key=key,
                    value=UserLimit(
                        requests=self.current_tokens - 1, time=current_time
                    ).json(),
                )
                return True

            bucket_limit = UserLimit.from_json(bucket)

            updated_tokens = self.count_new_tokens(
                current_time=current_time,
                last_time=bucket_limit.time,
                current_tokens=bucket_limit.requests,
                bucket_size=self.bucket_size,
                refill_rate=self.refill_rate,
            )

            if updated_tokens < 1:
                await storage.set_value(
                    key=key,
                    value=UserLimit(requests=updated_tokens, time=current_time).json(),
                )
                tokens_needed = 1 - updated_tokens
                seconds_to_wait = tokens_needed / self.refill_rate
                await answer_callback(
                    event, self.time_before_request, timedelta(seconds=seconds_to_wait)
                )
                return False

            await storage.set_value(
                key=key,
                value=UserLimit(requests=updated_tokens - 1, time=current_time).json(),
            )
            return True
