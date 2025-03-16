from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

from Utilites import create_main_menu_keyboard, delete_message

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, bot: Bot):
    """Handles the /start command."""
    keyboard = create_main_menu_keyboard()
    username = message.from_user.username

    start_message = await message.answer(
        "Привет! Я бот для поиска арендных квартир. Выберите действие:",
        reply_markup=keyboard,
    )

# --- Обработчик для кнопки "Главное меню" ---
@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, bot: Bot):
    """Handles the callback query for the "Main Menu" button."""
    # Используем функцию delete_message для удаления сообщения
    await delete_message(bot, callback.message.chat.id, callback.message.message_id)

    # Отправляем новое сообщение с главным меню
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Выберите действие:",
        reply_markup=create_main_menu_keyboard(),
    )
    await callback.answer()  # Подтверждаем callback