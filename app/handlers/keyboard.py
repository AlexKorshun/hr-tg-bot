from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Отменить")],
                    [KeyboardButton(text="Информация о компании")],
                    [KeyboardButton(text="Экскурсии по компании")],
                    [KeyboardButton(text="Виртуальные экскурсии по компании")],
                    [KeyboardButton(text="Организационная структура компании")],
                    [KeyboardButton(text="Столовая")],
                    [KeyboardButton(text="Корпоративные мероприятия")],
                    [KeyboardButton(text="Обучающие материалы")],
                    [KeyboardButton(text="Частозадаваемые вопросы")],
                    [KeyboardButton(text="Оформление документов")]


                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )

kbAdmin = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Добавить пользователя")],
                    [KeyboardButton(text="Отменить")],
                    [KeyboardButton(text="Информация о компании")],
                    [KeyboardButton(text="Экскурсии по компании")],
                    [KeyboardButton(text="Виртуальные экскурсии по компании")],
                    [KeyboardButton(text="Организационная структура компании")],
                    [KeyboardButton(text="Столовая")],
                    [KeyboardButton(text="Корпоративные мероприятия")],
                    [KeyboardButton(text="Обучающие материалы")],
                    [KeyboardButton(text="Частозадаваемые вопросы")],
                    [KeyboardButton(text="Оформление документов")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )