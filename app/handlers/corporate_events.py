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


async def show_events_info(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    sent = await message.answer(

'''
🎊 Корпоративные мероприятия НПП «ТЭК» 🎊

Текущие активности:

        «МаЁвка» — ежегодный корпоративный праздник для сотрудников и их семей 🎭

        «Корпора TEAM» — спортивные соревнования между отделами 🏆

        День рождения компании — торжественное мероприятие с награждением лучших сотрудников 🎖

        Квесты и тимбилдинги — регулярные командные активности 🧠

        Праздничные корпоративы — встречи по случаю профессиональных праздников 🍻

Как участвовать:

        Отслеживайте анонсы в боте

        Регистрируйтесь на интересующие мероприятия

        Приглашайте коллег присоединиться

Важные даты:

        Уточнить актуальные даты ближайших мероприятий можно у администратора

        Расписание обновляется каждую неделю

📋 Дополнительная информация:

        Подробности о каждом мероприятии

        Программа и условия участия

        Список участников

        Место проведения

Для получения подробной информации о конкретном мероприятии нажмите кнопку ниже ⬇️
''',
        reply_markup=builder.as_markup()
)
    await cache.add_message(user_id, sent)

    


