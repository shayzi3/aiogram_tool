from aiogram.types import CallbackQuery



async def callback(query: CallbackQuery) -> None:
     await query.answer("Button expired")