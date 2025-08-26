from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardButton
)

from app.handlers.file_manager import AdminActionCallback, isadmin

from app.uuid.uuid import new_uuid
from app.hash.hash import hash_string, verify_string

from app.repository.pg import *
from app.models.user import TelegramID, Role
from app.config import ROOT_ADMIN_ID
from app.cache import UserState

from app.handlers.start import *

router = Router()

async def show_excursions_info(message: types.Message, builder):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id



    builder.row(InlineKeyboardButton(text="Записаться на экскурсию", callback_data="sign_up_to_excursion"))
  
    fulltext = ""
    with open("files/face-to-face/title.txt", "r", encoding="utf-8") as title_file:
        fulltext = [line for line in title_file]

    sent = await message.answer(

    ''.join(fulltext),
        reply_markup=builder.as_markup()
)
    
    await cache.add_message(user_id, sent)
    

@router.callback_query(F.data == "sign_up_to_excursion")
async def handle_callback(callback_query: types.CallbackQuery):

    cache = callback_query.message.bot.user_state_cache
    user_id = callback_query.message.from_user.id

    total = await get_excursions_count()

    builder = InlineKeyboardBuilder()

    for i in range(total):
        excursion = await get_excursion_by_index(i)
        excursionID,dateTime,description = excursion
        dateTime_str = dateTime.strftime('%d-%m-%Y %H:%M:%S')
        date, time = dateTime_str.split()
        time = time.split(':')[:-1]  
        time = ':'.join(time) 
        builder.button(text=f"дата: {date} время: {time} Описание: {description} ", callback_data=f"excursion_{excursionID}")

    builder.adjust(1)

    sent = await callback_query.message.answer("⬇️ Выберите экскурсию:", reply_markup=builder.as_markup())
    await cache.add_message(user_id, sent)
    await callback_query.answer()  # Подтверждаем получение запроса
  


    
@router.callback_query(F.data.startswith('excursion_'))
async def handle_callback(callback_query: types.CallbackQuery):
    excursionID = int(callback_query.data.split("_")[-1])
    print(excursionID)
    print(callback_query.from_user.id) 
    await register_excursion(excursionID, callback_query.from_user.id)
    await callback_query.answer(text="Вы успешно записаны на экскурсию",show_alert=True)



