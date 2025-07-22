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


async def show_education_info(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    sent = await message.answer(

'''
📚 Обучающие материалы

Добро пожаловать в раздел обучающих материалов! Здесь вы найдете всё необходимое для успешной работы в компании.

Основные категории материалов:

    Welcome-курс

            Знакомство с компанией

            Корпоративные ценности и культура

            Правила безопасности

    Профессиональная подготовка

            Должностные инструкции

            Рабочие процедуры

            Стандарты качества

    Полезные ресурсы

            База знаний

            Часто задаваемые вопросы

            Контакты специалистов

    Как пользоваться:

            Выберите интересующий раздел

            Изучайте материалы в удобном темпе

            Сохраняйте важные документы

            Задавайте вопросы наставнику

Доступные форматы:

        📄 PDF-документы

        🎥 Видеоуроки

        🎯 Интерактивные тесты

        📝 Инструкции

Важно:

    Все материалы регулярно обновляются

    Доступ к материалам 24/7

    Поддержка в режиме реального времени

🔄 Для доступа к материалам выберите раздел ниже
''',
        reply_markup=builder.as_markup()
)
    await cache.add_message(user_id, sent)

    


