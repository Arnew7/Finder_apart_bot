from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database import get_all_apartments

router = Router()

@router.callback_query(F.data == "search")
async def search_apartment(callback: types.CallbackQuery):
    """
    Handles the 'search' callback query. Fetches all apartments and displays them in a formatted message.
    """
    all_apartments = get_all_apartments()

    if not all_apartments:
        await callback.answer("Квартиры не найдены.")
        return

    # Убираем лишние print() для отладки в продакшн коде.
    # Если нужно отлаживать, лучше использовать logging.
    # print("\nВсе квартиры:")
    # for apartment in all_apartments:
    #     print(apartment)

    message_text = "<b>Список всех квартир:</b>\n\n" # Заголовок

    for apartment in all_apartments:
        message_text += (
            f"<b>ID:</b> {apartment.get('id', 'N/A')}\n" # Более наглядно выделяем ID и другие поля
            f"<b>Username:</b> {apartment.get('username', 'N/A')}\n"
            f"<b>Город:</b> {apartment.get('city', 'N/A')}\n" # Переводим на русский для пользователя
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
            f"<b>Предоплата:</b> {apartment.get('prepayment', 'N/A')}\n\n" # Добавляем пустую строку для разделения квартир
        )

    try:
        await callback.message.edit_text(
            message_text,
            parse_mode="HTML" # Включаем HTML для форматирования
        )
    except Exception as e:
        error_message = f"Ошибка при редактировании сообщения со списком квартир: {e}"
        print(error_message) # В продакшн - замени на logging
        await callback.answer("Не удалось отобразить список квартир.") # Пользовательское сообщение
    else:
        await callback.answer("Список квартир обновлен.")  # Информативное сообщение после успешного обновления