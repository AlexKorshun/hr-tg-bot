from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import asyncio
import os

from app.config import ROOT_ADMIN_ID

router = Router()

class FileCallback(CallbackData, prefix="file"):
    folder: str
    file_name: str

@router.message(lambda message: message.document)
async def doc_download(message: types.Message, bot: Bot):
    if str(message.from_user.id) not in ROOT_ADMIN_ID:
        print(ROOT_ADMIN_ID, 'aaaaaaaaaa', str(message.from_user.id))
        await message.reply("НЕТ ДОСТУПА")
        return
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    
    typ = "ekskursii"

    dest = f"files/{typ}/{message.document.file_name}"

    await bot.download_file(file.file_path, dest)
    await message.reply("Загружовано")

@router.message(F.text.lower() == "ekskursii")
async def show_excursion_files(message: types.Message):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)

    print('amahere')
    folder_path = os.path.join("files", "ekskursii")

    if not os.path.exists(folder_path):
        sent = await message.answer("НЕ НАВДЕНО")
        await cache.add_message(user_id, sent)
        return

    builder = InlineKeyboardBuilder()

    for filename in os.listdir(folder_path):      
        builder.button(
            text=f"📄 {filename}",
            callback_data=FileCallback(folder="ekskursii", file_name=filename).pack()
        )
    
    builder.adjust(1)

    sent = await message.answer(
        "Выберите файл для загрузки:",
        reply_markup=builder.as_markup()
    )
    await cache.add_message(user_id, sent)

@router.callback_query(FileCallback.filter())
async def send_chosen_file(callback: types.CallbackQuery, callback_data: FileCallback, bot: Bot):
    folder = callback_data.folder
    filename = callback_data.file_name
    
    file_path = os.path.join("files", folder, filename)

    if not os.path.exists(file_path):
        await callback.answer(text="ФАЙЛА НЕТ", show_alert=True)
        return

    document_to_send = FSInputFile(file_path)

    try:
        await bot.send_document(
            chat_id=callback.from_user.id,
            document=document_to_send
        )
    except Exception as e:
        await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)
    finally:
        await callback.answer()
