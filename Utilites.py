# --- Utility Functions ---
import asyncio
from asyncio.log import logger

from aiogram import Bot, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def delete_message(bot: Bot, chat_id: int, message_id: int):
    """Deletes a message from the chat, handling potential errors."""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Сообщение {message_id} удалено из чата {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения {message_id} из чата {chat_id}: {e}")


def create_main_menu_keyboard():
    """Creates a simple inline keyboard for the main menu."""
    keyboard = [
        [types.InlineKeyboardButton(text="Добавить квартиру", callback_data="add")],
        [types.InlineKeyboardButton(text="Все квартиры", callback_data="search")],
        [types.InlineKeyboardButton(text="Поиск с фильтром", callback_data="search_filter")],
        [types.InlineKeyboardButton(text="Мои квартиры", callback_data="my_apart")],
    ]
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    return reply_markup


async def delayed_delete(bot: Bot, chat_id: int, message_id: int, delay: int = 5):
    """Deletes a message after a specified delay."""
    await asyncio.sleep(delay)
    await delete_message(bot, chat_id, message_id)


def create_prepayment_keyboard():
    """Создает клавиатуру для выбора необходимости предоплаты."""
    keyboard = [
        [InlineKeyboardButton(text="Да", callback_data="prepayment_yes"),
         InlineKeyboardButton(text="Нет", callback_data="prepayment_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_lift"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_parking_keyboard():
    """Создает клавиатуру для выбора наличия парковки."""
    keyboard = [
        [InlineKeyboardButton(text="Есть", callback_data="parking_yes"),
         InlineKeyboardButton(text="Нет", callback_data="parking_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_lift"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_lift_keyboard():
    """Создает клавиатуру для выбора наличия лифта."""
    keyboard = [
        [InlineKeyboardButton(text="Есть", callback_data="lift_yes"),
         InlineKeyboardButton(text="Нет", callback_data="lift_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_building_year"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_building_year_keyboard():
    """Создает клавиатуру для ввода года постройки."""
    keyboard = [[InlineKeyboardButton(text="Назад", callback_data="back_to_window_view"),
                 InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_window_view_keyboard():
    """Создает клавиатуру для выбора вида из окна."""
    keyboard = [
        [InlineKeyboardButton(text="Во двор", callback_data="view_yard"),
         InlineKeyboardButton(text="На улицу", callback_data="view_street")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_renovation"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_renovation_keyboard():
    """Создает клавиатуру для выбора необходимости ремонта."""
    keyboard = [
        [InlineKeyboardButton(text="Требуется", callback_data="renovation_yes"),
         InlineKeyboardButton(text="Не требуется", callback_data="renovation_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_balcony"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_balcony_keyboard():
    """Создает клавиатуру для выбора наличия балкона/лоджии."""
    keyboard = [
        [InlineKeyboardButton(text="Да", callback_data="balcony_yes"),
         InlineKeyboardButton(text="Нет", callback_data="balcony_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_bathroom"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Utility Functions ---
def create_back_menu_keyboard(back_callback: str):
    """Creates an inline keyboard with "Back" and "Main Menu" buttons."""
    keyboard = [
        [
            InlineKeyboardButton(text="Назад", callback_data=back_callback),
            InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_confirmation_keyboard():
    """Создает клавиатуру для подтверждения или редактирования данных."""
    keyboard = [
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm"),
         InlineKeyboardButton(text="Редактировать", callback_data="edit")],
        [InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_apartment_keyboard(index: int, total: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{index}"),
        InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{index}"),
        width=2
    )
    builder.row(InlineKeyboardButton(text="Написать владельцу", callback_data=f"contact_{index}"))
    builder.row(InlineKeyboardButton(text="Главное меню", callback_data="main_menu"))
    return builder.as_markup()



def create_apartment_keyboard(index):
    """Создает клавиатуру для анкеты квартиры."""
    keyboard = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data=f"left_{index}"),
            InlineKeyboardButton(text="Вперёд", callback_data=f"right_{index}"),
        ],
        [
            InlineKeyboardButton(text="Узнать юзера", callback_data=f"get_user_{index}"),
            InlineKeyboardButton(text="Главное меню", callback_data=f"main_menu")
        ]
    ])
    return keyboard
