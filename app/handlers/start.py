from aiogram import Router, types
from aiogram.filters import Command
from app import pg

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await pg.init_pool()
    user = await pg.get_user_by_id(message.from_user.id)

    if user:
        await message.answer(f"👋 С возвращением, {user['full_name']}!")
    else:
        full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        await pg.create_user(
            message.from_user.id,
            message.from_user.username,
            full_name
        )
        await message.answer("✅ Вы зарегистрированы!")
