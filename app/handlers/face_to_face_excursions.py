from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

from app.handlers.file_manager import AdminActionCallback
from app.uuid.uuid import new_uuid
from app.hash.hash import hash_string, verify_string

from app.repository.pg import *
from app.models.user import TelegramID, Role
from app.config import ROOT_ADMIN_ID
from app.cache import UserState

from app.handlers.start import *


async def show_excursions_info(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    # builder = InlineKeyboardBuilder()
    # callback_data_upload = AdminActionCallback(action="upload", category_name=category_name)
    # callback_data_view = AdminActionCallback(action="view", category_name=category_name)
    # callback_data_delete = AdminActionCallback(action="delete", category_name=category_name)
    
    # builder.button(text="📥 Загрузить файл", callback_data=callback_data_upload)
    # builder.button(text="📄 Посмотреть файлы", callback_data=callback_data_view)
    # builder.button(text="🗑️ Удалить файлы", callback_data=callback_data_delete)
    # builder.adjust(1)
 
    

    sent = await message.answer(

'''
список экскурсий и запись
'''
        ,reply_markup=builder.as_markup()
)
    await cache.add_message(user_id, sent)

    


