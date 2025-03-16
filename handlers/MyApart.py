import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Utilites import create_main_menu_keyboard, delete_message
from Database import delete_apartment, get_user_apartments

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# --- Handlers ---
router = Router()


async def show_user_apartments(username: str, bot: Bot, chat_id: int, apartments: list = None, current_index: int = 0):
    """Shows all apartments listed by a specific user with delete option, with pagination."""
    if apartments is None:
        apartments = get_user_apartments(username)

    if not apartments:
        await bot.send_message(
            chat_id,
            "У вас пока нет добавленных объявлений.",
            reply_markup=create_main_menu_keyboard(),
        )
        return

    if not (0 <= current_index < len(apartments)):
        await bot.send_message(
            chat_id,
            "Некорректный индекс квартиры.",
            reply_markup=create_main_menu_keyboard(),
        )
        return

    apartment = apartments[current_index]
    apartment_id = apartment[0]  # Assuming ID is the first column
    text = (
        f"Квартира ID: {apartment_id}\n"
        f"Город: {apartment[1]}\n"
        f"Район: {apartment[2]}\n"
        f"Улица: {apartment[3]}\n"
        f"Номер дома: {apartment[4]}\n"
        f"Подъезд: {apartment[5]}\n"
        f"Номер квартиры: {apartment[6]}\n"
        f"Комнат: {apartment[7]}\n"
        f"Этаж: {apartment[8]}\n"
        f"Этажность дома: {apartment[9]}\n"
        f"Цена аренды: {apartment[10]}\n"  # and so on, adjust indices
    )

    keyboard = [
        [
            InlineKeyboardButton(text="Назад", callback_data=f"prev_{current_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{len(apartments)}", callback_data="current_page"),
            InlineKeyboardButton(text="Вперед", callback_data=f"next_{current_index}"),
        ],
        [
            InlineKeyboardButton(
                text="Удалить", callback_data=f"delete_{apartment_id}"
            )
        ],
        [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    message = await bot.send_message(chat_id, text, reply_markup=reply_markup)


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def process_delete_apartment(callback_query: CallbackQuery, bot: Bot):
    """Handles the deletion of an apartment when the "Delete" button is pressed."""
    username = callback_query.from_user.username  # Получаем username
    apartment_id = int(callback_query.data.split("_")[1])

    logger.info(
        f"Попытка удаления квартиры ID: {apartment_id} пользователем: {username}"
    )

    try:
        if delete_apartment(apartment_id, username):
            await bot.send_message(
                callback_query.message.chat.id,
                f"Квартира ID {apartment_id} успешно удалена.",
                reply_markup=create_main_menu_keyboard(),
            )
            # Optionally, refresh the list of user's apartments after deletion
            apartments = get_user_apartments(username)
            if apartments:
                await show_user_apartments(username, bot, callback_query.message.chat.id, apartments=apartments)  # Обновляем список квартир

        else:
            await bot.send_message(
                callback_query.message.chat.id,
                "Не удалось удалить квартиру. Возможно, у вас нет прав.",
                reply_markup=create_main_menu_keyboard(),
            )
        # Удаляем сообщение с кнопкой "Удалить"
        await delete_message(
            bot, callback_query.message.chat.id, callback_query.message.message_id
        )

    except Exception as e:
        logger.exception(
            f"Ошибка при удалении квартиры ID {apartment_id} пользователем {username}: {e}"
        )
        await bot.send_message(
            callback_query.message.chat.id,
            "Произошла ошибка при удалении квартиры.",
            reply_markup=create_main_menu_keyboard(),
        )

    await callback_query.answer()  # Подтверждаем callback


@router.callback_query(F.data == "my_apart")
async def my_apart_handler(callback: CallbackQuery, bot: Bot):
    """Handles the callback query for the "My Apartments" button."""
    username = callback.from_user.username  # Получаем username
    chat_id = callback.message.chat.id
    logger.info(f"Показываем квартиры для пользователя: {username}")
    apartments = get_user_apartments(username)
    await show_user_apartments(username, bot, chat_id, apartments=apartments)

    # Удаляем сообщение с кнопкой "Мои квартиры"
    await delete_message(bot, callback.message.chat.id, callback.message.message_id)
    await callback.answer()  # Отвечаем на callback


@router.callback_query(lambda c: c.data.startswith("next_"))
async def next_page_callback(callback: CallbackQuery, bot: Bot):
    """Handles the next page button."""
    username = callback.from_user.username
    apartments = get_user_apartments(username)
    current_index = int(callback.data.split("_")[1])
    next_index = (current_index + 1) % len(apartments)  # Cycle through the apartments
    await delete_message(bot, callback.message.chat.id, callback.message.message_id)
    await show_user_apartments(username, bot, callback.message.chat.id, apartments=apartments, current_index=next_index)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("prev_"))
async def prev_page_callback(callback: CallbackQuery, bot: Bot):
    """Handles the previous page button."""
    username = callback.from_user.username
    apartments = get_user_apartments(username)
    current_index = int(callback.data.split("_")[1])
    prev_index = (current_index - 1) % len(apartments)  # Cycle through the apartments
    await delete_message(bot, callback.message.chat.id, callback.message.message_id)
    await show_user_apartments(username, bot, callback.message.chat.id, apartments=apartments, current_index=prev_index)
    await callback.answer()

@router.callback_query(F.data == "current_page")
async def current_page_handler(callback: CallbackQuery, bot: Bot):
    await callback.answer("Вы находитесь на текущей странице")