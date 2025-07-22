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



async def show_virtual_excursions(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    sent = await message.answer(

'''
🌏 Виртуальные экскурсии

Познакомьтесь с нашим предприятием в интерактивном формате!

Что вы найдёте в разделе:

    📽️ Видео-туры по производственным цехам

    🏢 Панорамы офисных помещений

    🎯 Экскурсии по важным объектам компании

    🎧 Аудиогиды с интересными фактами

👇 Нажмите кнопку ниже, чтобы скачать необходимый материал
''',
        reply_markup=builder.as_markup()
)
    await cache.add_message(user_id, sent)

    


