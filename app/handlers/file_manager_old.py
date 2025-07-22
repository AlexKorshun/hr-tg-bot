from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

import asyncio
import os

from app.config import ROOT_ADMIN_ID

from app.cache import UserState

router = Router()

class BrowserCallback(CallbackData, prefix="browse"):
    action: str
    index: int

class AdminActionCallback(CallbackData, prefix="admin_action"):
    action: str
    category_name: str

class AdminDeleteFileByIndex(CallbackData, prefix="admin_del_idx"):
    index: int

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

async def show_files_for_deletion(files_list: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for index, filename in enumerate(files_list):
        display_name = (filename[:30] + '..') if len(filename) > 32 else filename
        builder.button(text=display_name, callback_data="do_nothing")
        builder.button(text="❌", callback_data=AdminDeleteFileByIndex(index=index).pack())
    
    builder.adjust(2)
    return builder

@router.callback_query(AdminDeleteFileByIndex.filter())
async def delete_file_by_index_callback(callback: types.CallbackQuery, callback_data: AdminDeleteFileByIndex):
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id
    
    user_state, exist = await cache.get(user_id)

    if not exist or user_state.pending_action != "waiting_for_delete_choice":
        await callback.answer("Действие устарело. Пожалуйста, начните сначала.", show_alert=True)
        await callback.message.delete()
        return

    try:
        files_list = user_state.data["files"]
        category_name = user_state.data["category_name"]
        index_to_delete = callback_data.index
        
        filename_to_delete = files_list.pop(index_to_delete)
        file_path = os.path.join("files", category_name, filename_to_delete)
    
        if os.path.exists(file_path):
            os.remove(file_path)
            await callback.answer(f"Файл удален.")
        else:
            await callback.answer("Файл уже был удален.", show_alert=True)

        if files_list:
            user_state.data["files"] = files_list
            await cache.set(user_id, user_state)
            new_builder = await show_files_for_deletion(files_list)
            await callback.message.edit_reply_markup(reply_markup=new_builder.as_markup())
        else:
            await cache.delete(user_id)
            await callback.message.edit_text("Все файлы в этой категории удалены.")

    except (KeyError, IndexError):
        await callback.answer("Произошла ошибка. Попробуйте снова.", show_alert=True)
        await cache.delete(user_id)
        await callback.message.delete()

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

@router.callback_query(AdminActionCallback.filter())
async def handle_admin_action(callback: types.CallbackQuery, callback_data: AdminActionCallback):
    action = callback_data.action
    category_name = callback_data.category_name
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id

    if action == "view":
        root_path = os.path.join("files", category_name)
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        builder = await create_browser_keyboard_and_update_state(user_id, cache, root_path)
        
        if builder:
            await callback.message.edit_text(
                f"Содержимое категории «{category_name}»:",
                reply_markup=builder.as_markup()
            )
        else:
            await callback.message.edit_text(f"Категория «{category_name}» пуста.")
        
        await callback.answer()

    elif action == "upload":
        action_with_data = f"waiting_for_file_upload:{category_name}"
        await cache.update_action(user_id, action_with_data)
        await callback.message.edit_text("Теперь отправьте файл для загрузки.", parse_mode="HTML")
        await callback.answer()

    elif action == "delete":
        folder_path = os.path.join("files", category_name)
        if not os.path.exists(folder_path) or not os.listdir(folder_path):
            await callback.answer("В этой категории нет файлов для удаления.", show_alert=True)
            return

        files_to_delete = sorted(os.listdir(folder_path))

        action_name = "waiting_for_delete_choice"
        state_data = UserState(pending_action=action_name, role=None)
        
        state_data.data = {
            "files": files_to_delete,
            "category_name": category_name
        }
        await cache.set(user_id, state_data)

        builder = await show_files_for_deletion(files_to_delete)

        await callback.message.edit_text(
            "Нажмите на '❌', чтобы удалить файл:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()


# @router.callback_query(FileCallback.filter())
# async def send_chosen_file(callback: types.CallbackQuery, callback_data: FileCallback, bot: Bot):
#     cache = callback.bot.user_state_cache
#     user_id = callback.from_user.id

#     folder = callback_data.folder
#     filename = callback_data.file_name
    
#     file_path = os.path.join("files", folder, filename)

#     if not os.path.exists(file_path):
#         await callback.answer(text="ФАЙЛА НЕТ", show_alert=True)
#         return

#     document_to_send = FSInputFile(file_path)

#     try:
#         sent = await bot.send_document(
#             chat_id=callback.from_user.id,
#             document=document_to_send
#         )
#         await cache.add_message(user_id, sent)
#     except Exception as e:
#         await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)
#     finally:
#         await callback.answer()


async def create_browser_keyboard_and_update_state(
    user_id: int,
    cache: UserState,
    current_path: str,
    root_path: str,
) -> InlineKeyboardBuilder:
    """
    Создает клавиатуру и, что важно, обновляет состояние пользователя в кэше,
    сохраняя там текущий путь и список элементов.
    """
    builder = InlineKeyboardBuilder()

    # 1. Получаем списки папок и файлов
    dirs = sorted([d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))])
    files = sorted([f for f in os.listdir(current_path) if os.path.isfile(os.path.join(current_path, f))])

    # 2. Сохраняем все элементы в один список в кэше.
    # Это ключевой момент: теперь callback_data будет ссылаться на индекс в этом списке.
    items_on_screen = dirs + files
    
    # 3. Обновляем состояние пользователя в кэше
    user_state, _ = await cache.get(user_id)
    if not user_state: # Если состояние по какой-то причине пропало
        user_state = UserState(pending_action="browsing_files", role=None, data={})
    
    user_state.data['current_path'] = current_path
    user_state.data['root_path'] = root_path
    user_state.data['items'] = items_on_screen # Сохраняем список
    await cache.set(user_id, user_state)

    # 4. Создаем кнопки
    # Кнопка "Назад"
    if current_path != root_path:
        builder.button(
            text="⬅️ Назад",
            callback_data=BrowserCallback(action="back", index=-1).pack()
        )

    # Кнопки для папок
    for i, dirname in enumerate(dirs):
        builder.button(
            text=f"📁 {dirname}",
            callback_data=BrowserCallback(action="nav", index=i).pack()
        )

    # Кнопки для файлов
    for i, filename in enumerate(files):
        # Индекс файла будет смещен на количество папок
        file_index = len(dirs) + i
        builder.button(
            text=f"📄 {filename}",
            callback_data=BrowserCallback(action="send", index=file_index).pack()
        )

    builder.adjust(1)
    return builder


@router.callback_query(AdminActionCallback.filter(F.action == "view"))
async def start_file_browser(callback: types.CallbackQuery, callback_data: AdminActionCallback):
    """Начальная точка: пользователь нажал 'Посмотреть файлы'"""
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id
    category_name = callback_data.category_name
    
    root_path = os.path.join("files", category_name)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    if not os.listdir(root_path):
        await callback.answer("В этой категории пока нет файлов или папок.", show_alert=True)
        return

    builder = await create_browser_keyboard_and_update_state(
        user_id=user_id,
        cache=cache,
        current_path=root_path,
        root_path=root_path
    )

    await callback.message.edit_text("Файловый менеджер:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(BrowserCallback.filter())
async def handle_browser_navigation(callback: types.CallbackQuery, callback_data: BrowserCallback, bot: Bot):
    """Обрабатывает все нажатия в файловом менеджере."""
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id

    # Получаем состояние из кэша
    user_state, exist = await cache.get(user_id)
    if not exist or 'items' not in user_state.data or 'current_path' not in user_state.data:
        await callback.answer("Ваша сессия истекла, пожалуйста, начните заново.", show_alert=True)
        await callback.message.edit_text("Действие устарело.")
        return

    action = callback_data.action
    index = callback_data.index
    items_on_screen = user_state.data['items']
    current_path = user_state.data['current_path']
    root_path = user_state.data['root_path']

    if action == "back":
        path_to_open = os.path.dirname(current_path)
    else:
        # Проверяем, что индекс в пределах допустимого
        if not (0 <= index < len(items_on_screen)):
            await callback.answer("Ошибка: неверный выбор. Возможно, файлы изменились.", show_alert=True)
            return
        
        item_name = items_on_screen[index]
        path_to_open = os.path.join(current_path, item_name)

    # Если это файл - отправляем его
    if action == "send":
        # Доп. проверка, что это действительно файл
        if not os.path.isfile(path_to_open):
            await callback.answer("Ошибка: это не файл.", show_alert=True)
            return
        
        document_to_send = FSInputFile(path_to_open)
        try:
            await bot.send_document(chat_id=user_id, document=document_to_send)
        except Exception as e:
            await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)
        finally:
            await callback.answer() # Закрываем "часики"
        return # Отправка файла не меняет клавиатуру
    
    # Если это папка (nav или back) - обновляем клавиатуру
    elif action in ["nav", "back"]:
        # Доп. проверка, что это папка
        if not os.path.isdir(path_to_open):
            await callback.answer("Ошибка: папка не найдена.", show_alert=True)
            return

        builder = await create_browser_keyboard_and_update_state(
            user_id=user_id,
            cache=cache,
            current_path=path_to_open,
            root_path=root_path
        )
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer()


# @router.callback_query(ItemCallback.filter())
# async def handle_item_callback(callback: types.CallbackQuery, callback_data: ItemCallback, bot: Bot):
#     user_id = callback.from_user.id
#     cache = callback.bot.user_state_cache
    
#     # Получаем состояние пользователя
#     user_state, exist = await cache.get(user_id)
#     if not exist or "browse_paths" not in user_state.data:
#         await callback.message.edit_text("Ошибка: сессия навигации истекла. Пожалуйста, начните заново.")
#         await callback.answer(show_alert=True)
#         return

#     # Получаем список путей и нужный путь по индексу
#     paths = user_state.data["browse_paths"]
#     try:
#         selected_path = paths[callback_data.index]
#     except IndexError:
#         await callback.message.edit_text("Ошибка: неверный выбор. Пожалуйста, начните заново.")
#         await callback.answer(show_alert=True)
#         return

#     # --- Логика: определяем, папка это или файл ---
#     if os.path.isdir(selected_path):
#         # Если это папка, перерисовываем клавиатуру для нового пути
#         new_builder = await create_file_browser_keyboard(user_id, cache, selected_path)
#         if new_builder:
#             await callback.message.edit_text(
#                 f"Содержимое: <code>{selected_path}</code>",
#                 reply_markup=new_builder.as_markup(),
#                 parse_mode="HTML"
#             )
#         else:
#             # Обрабатываем случай, когда мы зашли в пустую папку
#             # Создаем клавиатуру только с кнопкой "Назад"
#             back_builder = await create_file_browser_keyboard(user_id, cache, selected_path)
#             await callback.message.edit_text(
#                 f"Папка <code>{selected_path}</code> пуста.",
#                 reply_markup=back_builder.as_markup() if back_builder else None,
#                 parse_mode="HTML"
#             )
#         await callback.answer()
    
#     elif os.path.isfile(selected_path):
#         # Если это файл, отправляем его
#         document_to_send = FSInputFile(selected_path)
#         try:
#             await bot.send_document(chat_id=user_id, document=document_to_send)
#         except Exception as e:
#             await callback.answer(f"Ошибка при отправке: {e}", show_alert=True)
#         finally:
#             await callback.answer()
    
#     else:
#         # Если путь больше не существует (файл удалили во время просмотра)
#         await callback.answer("Этот файл или папка больше не существует!", show_alert=True)
#         # Обновим текущее представление, чтобы убрать несуществующую кнопку
#         current_folder = os.path.dirname(paths[0]) # Определяем текущую папку
#         new_builder = await create_file_browser_keyboard(user_id, cache, current_folder)
#         await callback.message.edit_text(
#                 f"Содержимое: <code>{current_folder}</code>",
#                 reply_markup=new_builder.as_markup() if new_builder else None,
#                 parse_mode="HTML"
#             )

