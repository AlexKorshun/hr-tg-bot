from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
'''
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)'''
from app.uuid.uuid import new_uuid
from app.hash.hash import hash_string, verify_string

from app.repository.pg import *
from app.models.user import TelegramID, Role
from app.config import ROOT_ADMIN_ID
from app.cache import *

from app.handlers.keyboard import kb, kbAdmin

import app.metrics.metrics as metrics

async def start_cmd(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await init_pool()

    telegram_id = TelegramID(message.from_user.id)
    user = await get_user_by_id(telegram_id)

    if user:
        if str(message.from_user.id) in ROOT_ADMIN_ID:
            await message.answer(f"👋 С возвращением, {user.full_name}!", reply_markup=kbAdmin)
        else:
            await message.answer(f"👋 С возвращением, {user.full_name}!", reply_markup=kb)
    else:
        full_name = " ".join(
            filter(None, (message.from_user.first_name, message.from_user.last_name))
        )
        username = message.from_user.username or ""

        if str(message.from_user.id) in ROOT_ADMIN_ID:
            await create_user(
                telegram_id,
                username,
                full_name,
                role=Role.ADMIN,
                email=""
            )
            metrics.users_registered_total.inc()

            await message.answer("🛡️ Администратор зарегистрирован!", reply_markup=kb)
        else:
            await message.answer("Введите свою почту")
            await cache.update_action(user_id, "waiting_for_email_user")



async def handle_add_user_btn(message: types.Message, state: FSMContext):
    if str(message.from_user.id) not in ROOT_ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой функции.")
        return

    sent = await message.answer("✉️ Введите email нового пользователя:")
    
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    user_state, exists = await cache.get(user_id)
    if not exists:
        user_state = UserState(
            pending_action="",
            role=None,
            messages=[]
        )

    user_state.pending_action = "waiting_for_email_admin"
    user_state.messages.append(sent)
    await cache.set(user_id, user_state)


async def handle_admin_email_input(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)

    if str(message.from_user.id) not in ROOT_ADMIN_ID:
        sent = await message.answer("❌ У вас нет доступа к этой функции.")
        await cache.add_message(user_id, sent)
        return 
    email = message.text.strip()
    
    pass_string = new_uuid()

    hashed_pass_string = hash_string(pass_string)

    await create_hash(email, hashed_pass_string)


    await cache.delete(user_id)

    sent = await message.answer(f"📩 Строка для входа: {pass_string}")
    await cache.add_message(user_id, sent)

async def handle_email_user_input(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)
    email = message.text.strip()
    
    await state.update_data(email=email)  

    sent = await message.answer("Введите свой пароль(его можно получть у админа)")
    await cache.add_message(user_id, sent)

    await cache.update_action(user_id, "waiting_for_pass_string")


async def handle_password_user_input(message: types.Message, state: FSMContext):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)
    data = await state.get_data()
    email = str(data.get("email"))

    pass_string = message.text.strip()
    stored_hash = await get_pass_hash_by_email(email)


    if stored_hash is None:
        sent = await message.answer("❌ Нет такого пользователя.")
        await cache.add_message(user_id, sent)
        await cache.delete(user_id)
        return
    
    await cache.delete(user_id)
    password_hash, used = stored_hash
    if verify_string(pass_string, password_hash):
        full_name = " ".join(
            filter(None, (message.from_user.first_name, message.from_user.last_name))
        )
        username = message.from_user.username or ""

        role = await get_pass_role_by_email(email)
        await create_user(
                user_id,
                username,
                full_name,
                role=Role(role),
                email=email
            )
        metrics.users_registered_total.inc()
        sent = await message.answer("✅ Успешно зарегистрированы.")
        await cache.add_message(user_id, sent)
        await set_password_used(email)

        

        await message.answer(
'''👋 Добро пожаловать в корпоративный чат-бот!
Здесь вы можете:
📖 Получить информацию о компании, её структуре и мероприятиях
🧭 Записаться на экскурсии или пройти виртуальный тур
🎓 Изучить обучающие материалы и пройти тесты
📄 Узнать, как оформить отпуск, больничный или справки
❓ Найти ответы в разделе FAQ
💬 Оставить отзыв о процессе онбординга
⏰ Получать напоминания о встречах и важных задачах
🆘 Связаться со службой поддержки
Для начала выберите нужный раздел в меню или используйте кнопки ниже 👇''', reply_markup=kb)
    else:
        sent = await message.answer("❌ Неверный пароль.")
        await cache.add_message(user_id, sent)

    await state.clear()
