from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardButton
)
from app.handlers.FAQ import show_question_info
from app.handlers.help import show_help_info
from app.handlers.paperwork import show_paperwork_info
from app.handlers.canteen import show_canteen_info
from app.handlers.corporate_events import show_events_info
from app.handlers.education import show_education_info
from app.handlers.face_to_face_excursions import show_excursions_info
from app.handlers.organisational_structure import show_organisational_structure
from app.handlers.virtual_excursions import show_virtual_excursions
from app.uuid.uuid import new_uuid
from app.hash.hash import hash_string, verify_string

from app.repository.pg import *
from app.models.user import TelegramID, Role
from app.config import ROOT_ADMIN_ID
from app.cache import UserState

from app.handlers.start import *
from app.handlers.company_information import * 
from app.handlers.file_manager import *

import app.metrics.metrics as metrics

import base64

router = Router()


def isadmin(user_id):
    if str(user_id) in ROOT_ADMIN_ID:
        return True
    return False


@router.message(F.text.startswith("@"))
async def handle_inline_chat_search(message: types.Message):
    parts = message.text.split(maxsplit=3)
    
    if len(parts) < 4:
        await message.reply(
            "Неверный формат. \n"
            "Нажмите на кнопку «Поиск» в нужной категории, а затем допишите название файла.\n"
            "Например: `search canteen меню на неделю`"
        )
        return

    category_name = parts[2]
    query = parts[3].strip()

    if not query:
        await message.reply("Пожалуйста, укажите, что нужно найти после названия категории.")
        return

    await message.answer(f"Идет поиск по запросу «{query}» в категории «{category_name}»...")
    
    root_path = os.path.join("files", category_name)
    found_files = await perform_search(root_path, query, message.from_user.id)

    if not found_files:
        await message.answer(f"По вашему запросу ничего не найдено.")
    else:
        cache = message.bot.user_state_cache
        user_id = message.from_user.id
        
        user_state, exist = await cache.get(user_id)
        if not exist:
            user_state = UserState(pending_action="", role=None)
        
        user_state.data['search_results'] = found_files
        await cache.set(user_id, user_state)

        builder = InlineKeyboardBuilder()
        for i, file_path in enumerate(found_files):
            relative_path = os.path.relpath(file_path, "files")
            builder.button(
                text=f"📄 {relative_path}",
                callback_data=SearchFileCallback(index=i).pack()
            )
        builder.adjust(1)
        await message.answer("Вот что удалось найти:", reply_markup=builder.as_markup())


async def process_search_query(message: types.Message):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    query = message.text.strip()
    
    await cache.add_message(user_id, message)

    user_state, exist = await cache.get(user_id)
    if not exist or 'search_category' not in user_state.data:
        await message.answer("Произошла ошибка (категория не найдена). Пожалуйста, начните заново.")
        await cache.update_action(user_id, "")
        return

    category_name = user_state.data['search_category']
    
    await cache.update_action(user_id, "browsing_files")

    sent_msg = await message.answer(f"Идет поиск по запросу «{query}»...")
    await cache.add_message(user_id, sent_msg)
    
    root_path = os.path.join("files", category_name)
    found_files = await perform_search(root_path, query, message.from_user.id)

    if not found_files:
        sent_msg = await message.answer(f"По вашему запросу «{query}» ничего не найдено в категории «{category_name}».")
        await cache.add_message(user_id, sent_msg)
    else:
        builder = InlineKeyboardBuilder()
        for file_path in found_files:
            encoded_path = base64.urlsafe_b64encode(file_path.encode()).decode()
            relative_path = os.path.relpath(file_path, "files")
            print(encoded_path, relative_path, file_path)
            builder.button(
                text=f"📄 {relative_path}",
                callback_data=SearchFileCallback(path=encoded_path).pack()
            )
        builder.adjust(1)
        sent_msg = await message.answer("Вот что удалось найти:", reply_markup=builder.as_markup())
        await cache.add_message(user_id, sent_msg)


@router.message(Command("start"))
async def handle_start(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='/start').inc()
    await start_cmd(message, state)

@router.message(F.text == "Добавить пользователя")
async def handle_add_user(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Добавить пользователя').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.delete(user_id)

    await cache.add_message(user_id, message)

    await handle_add_user_btn(message, state)

@router.message(F.text == "Отменить")
async def handle_cancel(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Отменить').inc()

    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.add_message(user_id, message)

    await cache.delete(user_id)

@router.message(F.text == "Информация о компании")
async def handle_company_information(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Информация о компании').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=company_information,
        category_name="company_info",
        category_title=message.text
    )

@router.message(F.text == "Экскурсии по компании")
async def handle_show_excursions_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Экскурсии по компании').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    
    await handle_category_request(
        message,
        user_function=show_excursions_info,
        category_name="face-to-face",
        category_title=message.text
    )

@router.message(F.text == "Виртуальные экскурсии по компании")
async def handle_show_excursion_files(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Виртуальные экскурсии по компании').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    
    
    await handle_category_request(
        message,
        user_function=show_virtual_excursions,
        category_name="virt",
        category_title=message.text
    )

@router.message(F.text == "Организационная структура компании")
async def handle_show_organisational_structure(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Организационная структура компании').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=show_organisational_structure,
        category_name="org_structure",
        category_title=message.text
    )

@router.message(F.text == "Столовая")
async def handle_show_canteen_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Столовая').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    
    await handle_category_request(
        message,
        user_function=show_canteen_info,
        category_name="canteen",
        category_title=message.text
    )

@router.message(F.text == "Корпоративные мероприятия")
async def handle_show_corporative_events(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Корпоративные мероприятия').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=show_events_info,
        category_name="events",
        category_title=message.text
    )

@router.message(F.text == "Обучающие материалы")
async def handle_show_education_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Обучающие материалы').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=show_education_info,
        category_name="education",
        category_title=message.text
    )

@router.message(F.text == "Частозадаваемые вопросы")
async def handle_show_question_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Частозадаваемые вопросы').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id
    await cache.delete(user_id)
    await cache.add_message(user_id, message)
    await show_question_info(message, state)



@router.message(F.text == "Оформление документов")
async def handle_show_paperwork_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Оформление документов').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=show_paperwork_info,
        category_name="paperwork",
        category_title=message.text
    )

@router.message(F.text == "Помощь")
async def handle_show_help_info(message: types.Message, state: FSMContext):
    metrics.requests_total.labels(endpoint='Помощь').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await handle_category_request(
        message,
        user_function=show_help_info,
        category_name="help",
        category_title=message.text
    )


#############

async def handle_category_request(message: types.Message, user_function, category_name: str, category_title: str):
    cache = message.bot.user_state_cache
    user_id = message.from_user.id

    await cache.delete(user_id)
    await cache.add_message(user_id, message)
    
    if isadmin(user_id):
        builder = InlineKeyboardBuilder()
        callback_data_upload = AdminActionCallback(action="upload", category_name=category_name)
        callback_data_view = AdminActionCallback(action="view", category_name=category_name)
        callback_data_delete = AdminActionCallback(action="delete", category_name=category_name)
        
        builder.button(text="📥 Загрузить файл", callback_data=callback_data_upload)
        builder.button(text="📄 Посмотреть файлы", callback_data=callback_data_view)
        builder.button(text="🗑️ Удалить файлы", callback_data=callback_data_delete)
        builder.adjust(1)

        # sent_message = await message.answer(
        #     f"Выберите действие:",
        #     reply_markup=builder.as_markup(),
        #     parse_mode="HTML"
        # )
        # await cache.add_message(user_id, sent_message)


    else:
        builder = await show_files(category_name, message)
        search_command_text = f"/search {category_name} "
        
        builder.row(InlineKeyboardButton(text=" Поиск по этой категории", switch_inline_query_current_chat=search_command_text))

        # builder.button(
        #     text="🔎 Поиск по этой категории",
        #     switch_inline_query_current_chat=search_command_text
        # )

        files_builder = await show_files(category_name, message)
        
    await user_function(message, builder)

################


@router.message(F.content_type.in_({'document', 'photo', 'video'}))
async def handle_pending_files(message: types.Message):
    metrics.requests_total.labels(endpoint='[document]').inc()
    await process_admin_file_upload(message)

@router.message(F.text)
async def pending_dispatch(message: types.Message, state: FSMContext):
    if message.text.startswith('/search'):
        return

    metrics.requests_total.labels(endpoint='[text]').inc()
    cache = message.bot.user_state_cache
    user_id = message.from_user.id


    user_state, exist = await cache.get(user_id)
    if not exist:
        return
    
    action = user_state.pending_action

    if action and action.startswith("waiting_for_file_upload"):
        if message.text != "Отменить":
            sent = await message.answer("Отправьте файл или нажмите «Отменить».")
            await cache.add_message(user_id, sent)
        return

    match action:
        case "waiting_for_email_admin":
            await handle_admin_email_input(message, state)
        case "waiting_for_email_user":
            await handle_email_user_input(message, state)
        case "waiting_for_pass_string":
            await handle_password_user_input(message, state)
        case "waiting_for_search_query":
            await process_search_query(message)
        case _:
            sent = await message.answer("неправильное действие (если вы запутались нажмите ОТМЕНА и начните сначала)")
            await cache.add_message(user_id, sent)
