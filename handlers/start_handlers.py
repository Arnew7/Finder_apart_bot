from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, update, message

from handlers.add_apart_handler import AddApartment

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = [
        [types.InlineKeyboardButton(text="Добавить квартиру", callback_data='add')],
        [types.InlineKeyboardButton(text="Поиск квартир", callback_data='search')],
        [types.InlineKeyboardButton(text="Показать все квартиры", callback_data='show_all')]
    ]
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        'Привет! Я бот для поиска арендных квартир. '
        'Выберите действие:',
        reply_markup=reply_markup
    )

