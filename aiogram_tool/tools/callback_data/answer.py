from typing import Any

from aiogram.types import CallbackQuery



class CallbackDataAnswer:
     """Called when callback data for the button is not found."""
          
     async def __call__(self, query: CallbackQuery) -> Any:
          await query.answer(text="Button expired", show_alert=True)