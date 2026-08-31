from datetime import timedelta

from aiogram.types import TelegramObject


class RateLimitAnswer:
    """callback for handling the user moving outside the time window"""

    async def __call__(
        self, event: TelegramObject, window_time: timedelta, retry_after: timedelta
    ) -> None:
        """
        Args:
            event (TelegramObject): telegram event
            window_time (timedelta): time specified at the handler level
            retry_after (timedelta): time until the next request
        """
        await event.answer(
            text=f"Next request after {retry_after.total_seconds()} seconds."
        )
