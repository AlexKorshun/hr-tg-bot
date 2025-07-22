from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

import asyncio
import os

from app.config import ROOT_ADMIN_ID

router = Router()

class FileCallback(CallbackData, prefix="file"):
    folder: str
    file_name: str

class AdminActionCallback(CallbackData, prefix="admin_action"):
    action: str  # "upload" чи "view"
    category_name: str
    category_title: str

class AdminDeleteFileCallback(CallbackData, prefix="admin_delete"):
    category_name: str
    file_name: str


async def handle_doc_import(message: types.Message, bot: Bot, state: FSMContext):
    if str(message.from_user.id) not in ROOT_ADMIN_ID:
        print(ROOT_ADMIN_ID, '->', str(message.from_user.id))
        await message.reply("НЕТ ДОСТУПА")
        return
    file_id = message.document.file_id
    file = await bot.get_file(file_id)

    dest = f"files/{typ}/{message.document.file_name}"

    await bot.download_file(file.file_path, dest)
    await message.reply("Загружовано")

async def process_admin_file_upload(message: types.Message):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    user_state, exist = await cache.get(user_id)
    if not exist:
        return
        
    try:
        action, category_name = user_state.pending_action.split(':', 1)
    except (ValueError, AttributeError):
        return
        
    if action != "waiting_for_file_upload":
        return

    file_id = None
    file_name = f"file_{message.message_id}"

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{message.photo[-1].unique_id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{message.video.unique_id}.mp4"
    
    if not file_id: return

    dest_folder = os.path.join("files", category_name)
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, file_name)

    try:
        file_info = await message.bot.get_file(file_id)
        await message.bot.download_file(file_info.file_path, destination=dest_path)
        await message.answer(f"✅ Файл <code>{file_name}</code> успешно добавлен!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении файла: {e}")
    finally:
        await cache.delete(user_id)

async def show_files_for_deletion(category_name: str) -> InlineKeyboardBuilder | None:
    folder_path = os.path.join("files", category_name)

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        return None

    builder = InlineKeyboardBuilder()
    for filename in os.listdir(folder_path):
        builder.button(text=filename, callback_data="do_nothing")
        builder.button(text="❌ Удалить", callback_data=AdminDeleteFileCallback(category_name=category_name, file_name=filename).pack())
    
    builder.adjust(2)
    return builder

async def show_files(category_name: str, message: types.Message = None) -> InlineKeyboardBuilder | None:
    folder_path = os.path.join("files", category_name)

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        if message:
            cache = message.bot.user_state_cache
            user_id = message.from_user.id
            sent = await message.answer("В этой категории пока нет материалов.")
            await cache.add_message(user_id, sent)
        return None

    builder = InlineKeyboardBuilder()

    for filename in os.listdir(folder_path):      
        builder.button(
            text=f"📄 {filename}",
            callback_data=FileCallback(folder=category_name, file_name=filename).pack()
        )
    builder.adjust(1)
    return builder

# async def show_files(message: types.Message):
#     path = ""
#     if message.text == 'Виртуальные экскурсии по компании':
#         path = 'virt'
#     elif message.text == 'Столовая':
#         path = 'cantine'
#     elif message.text == 'Экскурсии по компании':
#         path = 'company_excursions'
#     elif message.text == 'Корпоративные мероприятия':
#         path = 'events'
#     elif message.text == 'Обучающие материалы':
#         path = 'education'
#     elif message.text == 'Организационная структура компании':
#         path = 'org_structure'
#     elif message.text == 'Информация о компании':
#         path = 'company_info'

        

#     cache = message.bot.user_state_cache
#     user_id = message.from_user.id
#     folder_path = os.path.join("files", path)

#     if not os.path.exists(folder_path):
#         sent = await message.answer("НЕ НАВДЕНО")
#         await cache.add_message(user_id, sent)
#         return

#     builder = InlineKeyboardBuilder()

#     for filename in os.listdir(folder_path):      
#         builder.button(
#             text=f"📄 {filename}",
#             callback_data=FileCallback(folder=path, file_name=filename).pack()
#         )
    
#     builder.adjust(1)
#     return builder

@router.callback_query(AdminDeleteFileCallback.filter())
async def delete_file_callback(callback: types.CallbackQuery, callback_data: AdminDeleteFileCallback):
    category_name = callback_data.category_name
    file_name = callback_data.file_name
    file_path = os.path.join("files", category_name, file_name)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            await callback.answer(f"Файл {file_name} удален.")
            
            new_builder = await show_files_for_admin(category_name)
            if new_builder:
                await callback.message.edit_reply_markup(reply_markup=new_builder.as_markup())
            else:
                await callback.message.edit_text("Все файлы в этой категории удалены.")

        else:
            await callback.answer("Этот файл уже был удален.", show_alert=True)

    except Exception as e:
        await callback.answer("Ошибка при удалении файла.", show_alert=True)

@router.callback_query(FileCallback.filter())
async def send_chosen_file(callback: types.CallbackQuery, callback_data: FileCallback, bot: Bot):
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id

    folder = callback_data.folder
    filename = callback_data.file_name
    
    file_path = os.path.join("files", folder, filename)

    if not os.path.exists(file_path):
        await callback.answer(text="ФАЙЛА НЕТ", show_alert=True)
        return

    document_to_send = FSInputFile(file_path)

    try:
        sent = await bot.send_document(
            chat_id=callback.from_user.id,
            document=document_to_send
        )
        await cache.add_message(user_id, sent)
    except Exception as e:
        await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)
    finally:
        await callback.answer()
