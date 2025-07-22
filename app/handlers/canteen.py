from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from app.uuid.uuid import new_uuid
from app.hash.hash import hash_string, verify_string

from app.repository.pg import *
from app.models.user import TelegramID, Role
from app.config import ROOT_ADMIN_ID
from app.cache import UserState

from app.handlers.start import *


async def show_canteen_info(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    sent = await message.answer(

'''
🍽 Столовая предприятия

Режим работы:

    Пн-Пт: 9:00 - 19:00

    Обеденный перерыв: 12:00 - 15:00 (основное время приема пищи)

    Сб-Вс: выходной

Важно:

    Оплата по корпоративной системе

    Места для всех сотрудников

    Свежие блюда ежедневно

👇 Нажмите кнопку ниже, чтобы скачать меню на сегодня
''',
        reply_markup=builder.as_markup()
)
    await cache.add_message(user_id, sent)

    


