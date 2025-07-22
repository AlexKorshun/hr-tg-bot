from aiogram import Bot, types, Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

import os
import shutil 
from app.config import ROOT_ADMIN_ID
from app.cache import UserStateCache, UserState

router = Router()

# CallbackData остается без изменений, мы просто добавим новые 'action'
class BrowserCallback(CallbackData, prefix="browse"):
    action: str
    index: int

class AdminActionCallback(CallbackData, prefix="admin_action"):
    action: str
    category_name: str

# Старые функции удаления больше не нужны, удаляем их.
# async def show_files_for_deletion(...) - УДАЛЕНО
# async def delete_file_by_index_callback(...) - УДАЛЕНО

# Ваша функция загрузки файлов. Я убрал ее дубликат.
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
    
    # Загрузка в подпапку
    dest_folder = os.path.join("files", category_name)
    if user_state.data and 'current_path' in user_state.data:
        dest_folder = user_state.data['current_path']

    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, file_name)

    try:
        file_info = await message.bot.get_file(file_id)
        await message.bot.download_file(file_info.file_path, destination=dest_path)
        await message.answer(f"✅ Файл <code>{file_name}</code> успешно добавлен в <code>{os.path.basename(dest_folder)}</code>!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении файла: {e}")
    finally:
        # Сбрасываем pending_action, чтобы можно было снова пользоваться меню
        user_state.pending_action = "browsing_files"
        await cache.set(user_id, user_state)


# --- МОДИФИЦИРОВАННАЯ КЛЮЧЕВАЯ ФУНКЦИЯ ---
async def create_browser_keyboard_and_update_state(
    user_id: int,
    cache: UserStateCache,
    current_path: str,
    root_path: str
) -> InlineKeyboardBuilder | None:
    if not os.path.exists(current_path) or not os.path.isdir(current_path):
        return None

    builder = InlineKeyboardBuilder()

    # 1. Получаем списки папок и файлов
    dirs = sorted([d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))])
    files = sorted([f for f in os.listdir(current_path) if os.path.isfile(os.path.join(current_path, f))])
    items_on_screen = dirs + files

    # 2. Обновляем состояние в кэше
    user_state, _ = await cache.get(user_id)
    if not user_state:
        user_state = UserState(pending_action="browsing_files", role=None, data={})
    
    user_state.data['current_path'] = current_path
    user_state.data['root_path'] = root_path
    user_state.data['items'] = items_on_screen
    # Получаем режим, по умолчанию 'view'
    mode = user_state.data.get('mode', 'view')
    await cache.set(user_id, user_state)

    # 3. Создаем кнопки в зависимости от режима
    if mode == 'delete':
        # --- Клавиатура для режима удаления ---
        builder.button(text="↩️ Завершить удаление", callback_data=BrowserCallback(action="cancel_delete", index=-1).pack())
        for i, item_name in enumerate(items_on_screen):
            icon = "📁" if i < len(dirs) else "📄"
            # Две кнопки в строке: имя и кнопка удаления
            builder.button(text=f"{icon} {item_name}", callback_data=BrowserCallback(action="info", index=i).pack())
            builder.button(text="❌ Удалить", callback_data=BrowserCallback(action="delete", index=i).pack())
        builder.adjust(1, 2) # Кнопка отмены - одна, остальные по две
    else:
        # --- Клавиатура для обычного режима просмотра ---
        if current_path != root_path:
            builder.button(text="⬅️ Назад", callback_data=BrowserCallback(action="back", index=-1).pack())

        for i, dirname in enumerate(dirs):
            builder.button(text=f"📁 {dirname}", callback_data=BrowserCallback(action="nav", index=i).pack())

        for i, filename in enumerate(files):
            file_index = len(dirs) + i
            builder.button(text=f"📄 {filename}", callback_data=BrowserCallback(action="send", index=file_index).pack())
        builder.adjust(1)

    has_buttons = any(True for _ in builder.buttons)
    return builder if has_buttons else None


# --- ОБНОВЛЕННЫЙ ОБРАБОТЧИК АДМИНСКИХ ДЕЙСТВИЙ ---
@router.callback_query(AdminActionCallback.filter())
async def handle_admin_action(callback: types.CallbackQuery, callback_data: AdminActionCallback):
    action = callback_data.action
    category_name = callback_data.category_name
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id

    root_path = os.path.join("files", category_name)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    if action == "view":
        user_state, _ = await cache.get(user_id)
        if user_state:
            user_state.data['mode'] = 'view'
            await cache.set(user_id, user_state)
        
        builder = await create_browser_keyboard_and_update_state(user_id, cache, root_path, root_path)
        if builder:
            await callback.message.edit_text(f"Просмотр: <code>{category_name}</code>", reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            await callback.message.edit_text(f"Категория «{category_name}» пуста.")

    elif action == "upload":
        user_state, _ = await cache.get(user_id)
        current_path = user_state.data.get('current_path', root_path) if user_state and user_state.data else root_path
        
        await cache.update_action(user_id, f"waiting_for_file_upload:{category_name}")
        
        folder_name = os.path.basename(current_path)
        await callback.message.edit_text(f"Отправьте файл для загрузки в папку <code>{folder_name}</code>.", parse_mode="HTML")

    elif action == "delete":
        # Активируем режим удаления
        user_state, _ = await cache.get(user_id)
        if not user_state:
             user_state = UserState(pending_action="browsing_files", role=None, data={})
        user_state.data['mode'] = 'delete'
        await cache.set(user_id, user_state)

        builder = await create_browser_keyboard_and_update_state(user_id, cache, root_path, root_path)
        if builder:
            await callback.message.edit_text(f"<b>Режим удаления.</b>\nВыберите объект для удаления в категории <code>{category_name}</code>:", reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            await callback.message.edit_text(f"Нечего удалять в категории «{category_name}».")

    await callback.answer()

# --- ОБНОВЛЕННЫЙ ОБРАБОТЧИК НАВИГАЦИИ ---
@router.callback_query(BrowserCallback.filter())
async def handle_browser_navigation(callback: types.CallbackQuery, callback_data: BrowserCallback, bot: Bot):
    cache = callback.bot.user_state_cache
    user_id = callback.from_user.id

    user_state, exist = await cache.get(user_id)
    if not exist or 'items' not in user_state.data or 'current_path' not in user_state.data:
        await callback.answer("Ваша сессия истекла, начните заново.", show_alert=True)
        await callback.message.delete()
        return

    action = callback_data.action
    index = callback_data.index
    current_path = user_state.data['current_path']
    root_path = user_state.data['root_path']
    items_on_screen = user_state.data.get('items', [])

    path_to_open = ""
    if action not in ['back', 'cancel_delete', 'info']:
        if not (0 <= index < len(items_on_screen)):
            await callback.answer("Ошибка: неверный выбор.", show_alert=True)
            return
        item_name = items_on_screen[index]
        path_to_open = os.path.join(current_path, item_name)

    # --- Новые и обновленные действия ---
    if action == "delete":
        try:
            if os.path.isfile(path_to_open):
                os.remove(path_to_open)
                await callback.answer(f"Файл '{os.path.basename(path_to_open)}' удален.")
            elif os.path.isdir(path_to_open):
                shutil.rmtree(path_to_open)
                await callback.answer(f"Папка '{os.path.basename(path_to_open)}' и ее содержимое удалены.")
            else:
                await callback.answer("Объект уже удален.", show_alert=True)
            
            # Обновляем клавиатуру после удаления
            builder = await create_browser_keyboard_and_update_state(user_id, cache, current_path, root_path)
            if builder:
                await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
            else:
                await callback.message.edit_text(f"Папка <code>{os.path.basename(current_path)}</code> пуста.")

        except Exception as e:
            await callback.answer(f"Ошибка при удалении: {e}", show_alert=True)
        return

    elif action == "cancel_delete":
        user_state.data['mode'] = 'view'
        await cache.set(user_id, user_state)
        builder = await create_browser_keyboard_and_update_state(user_id, cache, current_path, root_path)
        await callback.message.edit_text(f"Просмотр: <code>{os.path.basename(current_path)}</code>", reply_markup=builder.as_markup(), parse_mode="HTML")
        await callback.answer("Режим удаления отменен.")
        return
    
    elif action == "info":
        await callback.answer("Нажмите '❌ Удалить' для удаления.")
        return

    # --- Старые действия ---
    if action == "back":
        path_to_open = os.path.dirname(current_path)
    
    if action == "send":
        if not os.path.isfile(path_to_open):
            await callback.answer("Ошибка: это не файл.", show_alert=True)
            return
        await bot.send_document(chat_id=user_id, document=FSInputFile(path_to_open))
        await callback.answer()
        return

    elif action in ["nav", "back"]:
        if not os.path.isdir(path_to_open):
            await callback.answer("Ошибка: папка не найдена.", show_alert=True)
            return
        
        builder = await create_browser_keyboard_and_update_state(user_id, cache, path_to_open, root_path)
        if builder:
            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        else:
            await callback.message.edit_text(f"Папка <code>{os.path.basename(path_to_open)}</code> пуста.")
        await callback.answer()

# Адаптированная функция для ОБЫЧНЫХ пользователей (не админов)
# Она не дает навигации по папкам, только показывает файлы в корне категории
async def show_files(category_name: str, message: types.Message) -> InlineKeyboardBuilder | None:
    folder_path = os.path.join("files", category_name)
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        sent = await message.answer("В этой категории пока нет материалов.")
        await cache.add_message(user_id, sent)
        return None

    # Для обычных пользователей просто создаем клавиатуру с файлами
    builder = await create_browser_keyboard_and_update_state(
        user_id, cache, folder_path, folder_path
    )

    return builder