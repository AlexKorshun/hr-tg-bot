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

router = Router()


class AddUser(StatesGroup):
    waiting_for_email_admin = State()
    waiting_for_email_user = State()
    waiting_for_pass_string = State()


@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await init_pool()

    telegram_id = TelegramID(message.from_user.id)
    user = await get_user_by_id(telegram_id)

    if user:
        if str(message.from_user.id) == str(ROOT_ADMIN_ID):
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Добавить пользователя")]
                ],
                resize_keyboard=True
            )
            await message.answer(f"👋 С возвращением, {user.full_name}!", reply_markup=kb)
        else:
            await message.answer(f"👋 С возвращением, {user.full_name}!")
    else:
        full_name = " ".join(
            filter(None, (message.from_user.first_name, message.from_user.last_name))
        )
        username = message.from_user.username or ""

        if str(message.from_user.id) == str(ROOT_ADMIN_ID):
            await create_user(
                telegram_id,
                username,
                full_name,
                role=Role.ADMIN,
                email=""
            )
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Добавить пользователя")]
                ],
                resize_keyboard=True
            )
            await message.answer("🛡️ Администратор зарегистрирован!", reply_markup=kb)
        else:
            await message.answer("Введите свою почту")
            await state.set_state(AddUser.waiting_for_email_user)



@router.message(F.text == "Добавить пользователя")
async def handle_add_user_btn(message: types.Message, state: FSMContext):
    if str(message.from_user.id) != str(ROOT_ADMIN_ID):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return

    await message.answer("✉️ Введите email нового пользователя:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddUser.waiting_for_email_admin)


@router.message(AddUser.waiting_for_email_admin, F.text)
async def handle_admin_email_input(message: types.Message, state: FSMContext):
    if str(message.from_user.id) != str(ROOT_ADMIN_ID):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return 
    email = message.text.strip()
    
    pass_string = new_uuid()

    hashed_pass_string = hash_string(pass_string)

    await create_hash(email, hashed_pass_string)


    await message.answer(f"📩 Строка для входа: {pass_string}")
    await state.clear()

@router.message(AddUser.waiting_for_email_user, F.text)
async def handle_email_user_input(message: types.Message, state: FSMContext):
    email = message.text.strip()
    
    await state.update_data(email=email)  

    await message.answer("Введите свой пароль(его можно получть у админа)")
    await state.set_state(AddUser.waiting_for_pass_string)



@router.message(AddUser.waiting_for_pass_string, F.text)
async def handle_password_user_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = str(data.get("email"))

    pass_string = message.text.strip()
    stored_hash = await get_pass_hash_by_email(email)


    if stored_hash is None:
        await message.answer("❌ Нет такого пользователя.")
        await state.clear()
        return
    
    if verify_string(str(pass_string), str(stored_hash["password_hash"])):
        await create_user(
            telegram_id=TelegramID(message.from_user.id),
            username=message.from_user.username or "",
            full_name=" ".join(
                filter(None, (message.from_user.first_name, message.from_user.last_name))
            ),
            role=Role.CANDIDATE,
            email=email,
        )
        await message.answer("✅ Успешно зарегистрированы.")
    else:
        await message.answer("❌ Неверный пароль.")

    await state.clear()
