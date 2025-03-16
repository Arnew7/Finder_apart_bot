from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from Utilites import create_main_menu_keyboard, delete_message



from Database import get_all_apartments

router = Router()


async def format_apartment_message(apartment: dict) -> str:
    """Форматирует сообщение с информацией об одной квартире."""
    return (
        f"<b>ID:</b> {apartment.get('id', 'N/A')}\n"
        f"<b>Username:</b> {apartment.get('username', 'N/A')}\n"
        f"<b>Город:</b> {apartment.get('city', 'N/A')}\n"
        f"<b>Район:</b> {apartment.get('district', 'N/A')}\n"
        f"<b>Улица:</b> {apartment.get('street', 'N/A')}\n"
        f"<b>Дом:</b> {apartment.get('house', 'N/A')}\n"
        f"<b>Номер квартиры:</b> {apartment.get('apartment_number', 'N/A')}\n"
        f"<b>Комнат:</b> {apartment.get('room', 'N/A')}\n"
        f"<b>Этаж:</b> {apartment.get('floor', 'N/A')}\n"
        f"<b>Этажность:</b> {apartment.get('total_floors', 'N/A')}\n"
        f"<b>Цена:</b> {apartment.get('price', 'N/A')}\n"
        f"<b>Площадь:</b> {apartment.get('total_area', 'N/A')}\n"
        f"<b>Высота потолков:</b> {apartment.get('ceiling_height', 'N/A')}\n"
        f"<b>Балкон:</b> {apartment.get('balcony', 'N/A')}\n"
        f"<b>Вид из окна:</b> {apartment.get('window_view', 'N/A')}\n"
        f"<b>Год постройки:</b> {apartment.get('building_year', 'N/A')}\n"
        f"<b>Лифт:</b> {apartment.get('lift', 'N/A')}\n"
        f"<b>Парковка:</b> {apartment.get('parking', 'N/A')}\n"
        f"<b>Предоплата:</b> {apartment.get('prepayment', 'N/A')}\n"
    )


async def send_apartment(callback: types.CallbackQuery, apartments: list, index: int, state: FSMContext):
    """Отправляет или редактирует сообщение с информацией о квартире и кнопками."""
    if 0 <= index < len(apartments):
        apartment = apartments[index]
        message_text = await format_apartment_message(apartment)

        keyboard = [
            [
                InlineKeyboardButton(text="Назад", callback_data="prev_apartment"),
                InlineKeyboardButton(text=f"{index + 1}/{len(apartments)}", callback_data="current_apartment"),
                InlineKeyboardButton(text="Вперед", callback_data="next_apartment"),
            ],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)


        try:
            await callback.message.edit_text(
                f"<b>Квартира {index + 1} из {len(apartments)}</b>\n\n" + message_text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Ошибка при отправке/редактировании сообщения: {e}")
            await callback.answer("Не удалось отобразить квартиру.")
        else:
            await state.update_data(current_apartment_index=index)  # Обновляем индекс в state
            await callback.answer()  # Просто убираем "часики"

    else:
        await callback.message.edit_text("<b>Квартиры закончились.</b>\nНачните поиск заново, если хотите посмотреть еще раз.", parse_mode="HTML",reply_markup=create_main_menu_keyboard())
        await state.clear()  # Очищаем состояние, так как квартиры закончились


@router.callback_query(F.data == "search")
async def search_apartment(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для callback_query "search".
    Начинает показ квартир.
    """
    all_apartments = get_all_apartments()

    if not all_apartments:
        await callback.answer("Квартиры не найдены.", reply_markup=create_main_menu_keyboard())
        return

    await state.update_data(apartments=all_apartments)  # Сохраняем список квартир в state
    await send_apartment(callback, all_apartments, 0, state)  # Отправляем первую квартиру


@router.callback_query(F.data == "next_apartment")
async def next_apartment_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для кнопки "Вперед" (следующая квартира)."""
    data = await state.get_data()
    apartments = data.get("apartments")
    current_index = data.get("current_apartment_index", 0)

    if not apartments:
        await callback.answer("Список квартир не найден. Начните поиск заново.",reply_markup=create_main_menu_keyboard())
        return

    next_index = current_index + 1
    if next_index >= len(apartments):
        next_index = 0  # go to begin
    await send_apartment(callback, apartments, next_index, state)


@router.callback_query(F.data == "prev_apartment")  # Обработчик для кнопки "Назад" (предыдущая)
async def prev_apartment_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для кнопки "Назад" (предыдущая квартира)."""
    data = await state.get_data()
    apartments = data.get("apartments")
    current_index = data.get("current_apartment_index", 0)

    if not apartments:
        await callback.answer("Список квартир не найден. Начните поиск заново.", reply_markup=create_main_menu_keyboard())
        return

    prev_index = current_index - 1
    if prev_index < 0:
        prev_index = len(apartments) - 1  # go to end
    await send_apartment(callback, apartments, prev_index, state)


@router.callback_query(F.data == "current_apartment")
async def current_apartment_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Вы находитесь на текущей странице")


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, bot: Bot):
    """Handles the callback for the main menu button."""
    await bot.send_message(callback.message.chat.id, "Вы вернулись в главное меню.", reply_markup=create_main_menu_keyboard())
    await callback.message.delete()  # delete current message
    await callback.answer()  # Acknowledge the callback