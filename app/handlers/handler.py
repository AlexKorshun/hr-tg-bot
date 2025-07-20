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
from app.handlers.company_information import * 

router = Router()


@router.message(Command("start"))
async def handle_start(message: types.Message, state: FSMContext):
    await start_cmd(message, state)

@router.message(F.text == "Добавить пользователя")
async def handle_add_user(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.delete(user_id)

    await cache.add_message(user_id, message)

    await handle_add_user_btn(message, state)

@router.message(F.text == "Отменить")
async def handle_cancel(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)

    await cache.delete(user_id)

@router.message(F.text == "Информация о компании")
async def hande_company_information(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.delete(user_id)

    await cache.add_message(user_id, message)

    await company_information(message, state)



@router.message(F.text)
async def pending_dispatch(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id


    user_state, exist = await cache.get(user_id)
    if not exist:
        return
    
    action = user_state.pending_action
    match action:
        case "waiting_for_email_admin":
            await handle_admin_email_input(message, state)
        case "waiting_for_email_user":
            await handle_email_user_input(message, state)
        case "waiting_for_pass_string":
            await handle_password_user_input(message, state)
        case _:
            sent = await message.answer("неправильное действие (если вы запутались нажмите ОТМЕНА и начните сначала)")
            cache.add_message(user_id, sent)
