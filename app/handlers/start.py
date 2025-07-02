from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import User

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    async with SessionLocal() as session:
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

        result = await session.execute(select(User).where(User.telegram_id == user_id))
        if result.scalar():
            await message.answer("👋 С возвращением!")
        else:
            user = User(telegram_id=user_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
            await message.answer("✅ Вы зарегистрированы в системе WW ТЭК!")