from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from Utilites import create_back_menu_keyboard, create_main_menu_keyboard, delayed_delete, delete_message, \
    create_apartment_keyboard
import asyncio
import re
from Database import fetch_apartments, get_username_by_apartment_id  # Импортируйте функцию из вашего модуля Database

router = Router()


class SearchApartment(StatesGroup):
    waiting_for_city = State()
    waiting_for_price_min = State()
    waiting_for_price_max = State()
    waiting_for_rooms_min = State()
    waiting_for_rooms_max = State()
    waiting_for_floor_min = State()
    waiting_for_floor_max = State()
    confirm_search = State()
    showing_results = State()  # Добавляем состояние для показа результатов


async def format_apartment_message(apartment: dict) -> str:
    """Форматирует сообщение с информацией об одной квартире."""
    return (
        f"<b>Город:</b> {apartment.get('city', 'N/A')}\n"
        f"<b>Район:</b> {apartment.get('district', 'N/A')}\n"
        f"<b>Улица:</b> {apartment.get('street', 'N/A')}\n"
        f"<b>Цена:</b> {apartment.get('price', 'N/A')}\n"
        f"<b>Комнат:</b> {apartment.get('room', 'N/A')}\n"
        f"<b>Этаж:</b> {apartment.get('floor', 'N/A')}\n"
        f"<b>Общая площадь:</b> {apartment.get('total_area', 'N/A')}\n"
    )


async def send_apartment(chat_id, apartments, index, state: FSMContext, bot: Bot, message_id=None):
    """Отправляет или редактирует сообщение с информацией о квартире."""
    if not apartments:
        await bot.send_message(chat_id, "Квартиры не найдены.")
        return

    if index < 0:
        index = 0
    elif index >= len(apartments):
        index = len(apartments) - 1

    apartment = apartments[index]

    # Формируем текст сообщения с информацией о квартире (как и раньше)
    message_text = f"Квартира #{index + 1} из {len(apartments)}\n\n"
    message_text += f"Город: {apartment['city']}\n"
    message_text += f"Район: {apartment['district']}\n"
    message_text += f"Улица: {apartment['street']}\n"
    message_text += f"Дом: {apartment['house']}\n"
    message_text += f"Подъезд: {apartment['entrance']}\n"
    message_text += f"Номер квартиры: {apartment['apartment_number']}\n"
    message_text += f"Комнат: {apartment['room']}\n"
    message_text += f"Этаж: {apartment['floor']}\n"
    message_text += f"Этажность: {apartment['total_floors']}\n"
    message_text += f"Цена: {apartment['price']}\n"
    message_text += f"Депозит: {apartment['deposit']}\n"
    message_text += f"Общая площадь: {apartment['total_area']}\n"
    message_text += f"Высота потолков: {apartment['ceiling_height']}\n"
    message_text += f"Санузел: {apartment['bathroom']}\n"
    message_text += f"Балкон: {apartment['balcony']}\n"
    message_text += f"Ремонт: {apartment['renovation']}\n"
    message_text += f"Вид из окна: {apartment['window_view']}\n"
    message_text += f"Год постройки: {apartment['building_year']}\n"
    message_text += f"Лифт: {apartment['lift']}\n"
    message_text += f"Парковка: {apartment['parking']}\n"
    message_text += f"Предоплата: {apartment['prepayment']}\n"

    # Создаем клавиатуру, используя новую функцию
    keyboard = create_apartment_keyboard(index)

    # Отправляем или редактируем сообщение
    if message_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message_text,
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard) # Отправляем новое, если не удалось отредактировать
    else:
        message = await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard)
        message_id = message.message_id

    await state.update_data(current_apartment_index=index, current_apartment_message_id=message_id)


@router.callback_query(lambda c: c.data.startswith("left_"))
@router.callback_query(lambda c: c.data.startswith("right_"))
async def handle_navigation(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик кнопок "влево" и "вправо". Удаляет сообщение и показывает следующее/предыдущее."""
    action, index = callback.data.split("_")
    index = int(index)
    data = await state.get_data()
    apartments = data.get("apartments", [])
    current_index = data.get("current_apartment_index", 0)
    current_apartment_message_id = data.get("current_apartment_message_id")

    try:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    if action == "right":
        next_index = current_index + 1
    else:
        next_index = current_index - 1

    # Вызываем функцию send_apartment с новым индексом для отображения следующей квартиры
    await send_apartment(
        chat_id=callback.message.chat.id,
        apartments=apartments,
        index=next_index,
        state=state,
        bot=bot,
        message_id=current_apartment_message_id # Передаем message_id для редактирования сообщения
    )

    await callback.answer()










@router.callback_query(F.data == "search_filter")
async def search_apartment_start(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Начало поиска квартиры."""
    await state.clear()
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    msg = await callback_query.message.answer("Укажите город для поиска:", reply_markup=reply_markup)

    await state.update_data(start_message_id=msg.message_id)  # Сохраняем ID сообщения для редактирования
    await state.set_state(SearchApartment.waiting_for_city)
    await delete_message(bot, callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer()


@router.message(SearchApartment.waiting_for_city, F.text)
async def search_city_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода города для поиска."""
    city = message.text.strip()
    if not re.match(r"^[а-яА-ЯёЁ\s-]+$", city):
        error_msg = await message.reply(
            "Пожалуйста, используйте только русские буквы, пробелы и дефисы.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    if len(city) > 50:
        error_msg = await message.reply(
            "Слишком длинное название города. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    elif len(city) < 2:
        error_msg = await message.reply(
            "Слишком короткое название города. Пожалуйста, введите длиннее.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    await state.update_data(city=city)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
        # Обработка случая, когда сообщение не может быть удалено (например, если оно было отправлено слишком давно)

    reply_markup = create_back_menu_keyboard("back_to_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите минимальную цену (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_price_min)


@router.message(SearchApartment.waiting_for_price_min, F.text)
async def search_price_min_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода минимальной цены."""
    try:
        price_min = float(message.text)
        if price_min < 0:
            error_msg = await message.reply("Минимальная цена не может быть отрицательной. Пожалуйста, введите корректную цену.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите минимальную цену цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(price_min=price_min)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    reply_markup = create_back_menu_keyboard("back_to_city_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите максимальную цену (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_price_max)


@router.message(SearchApartment.waiting_for_price_max, F.text)
async def search_price_max_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода максимальной цены."""
    try:
        price_max = float(message.text)
        price_min = (await state.get_data()).get("price_min", 0)
        if price_max < 0:
            error_msg = await message.reply("Максимальная цена не может быть отрицательной. Пожалуйста, введите корректную цену.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
        if price_max != 0 and price_max < price_min:
            error_msg = await message.reply(
                "Максимальная цена не может быть меньше минимальной. Пожалуйста, введите корректную цену."
            )
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите максимальную цену цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(price_max=price_max)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    reply_markup = create_back_menu_keyboard("back_to_price_min_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите минимальное количество комнат (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_rooms_min)


@router.message(SearchApartment.waiting_for_rooms_min, F.text)
async def search_rooms_min_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода минимального количества комнат."""
    try:
        rooms_min = int(message.text)
        if rooms_min < 0:
            error_msg = await message.reply(
                "Минимальное количество комнат не может быть отрицательным. Пожалуйста, введите корректное число."
            )
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите минимальное количество комнат цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(rooms_min=rooms_min)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    reply_markup = create_back_menu_keyboard("back_to_price_max_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите максимальное количество комнат (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )
    await state.set_state(SearchApartment.waiting_for_rooms_max)


@router.message(SearchApartment.waiting_for_rooms_max, F.text)
async def search_rooms_max_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода максимального количества комнат."""
    try:
        rooms_max = int(message.text)
        rooms_min = (await state.get_data()).get("rooms_min", 0)

        if rooms_max < 0:
            error_msg = await message.reply(
                "Максимальное количество комнат не может быть отрицательным. Пожалуйста, введите корректное число.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

        if rooms_max != 0 and rooms_max < rooms_min:
            error_msg = await message.reply(
                "Максимальное количество комнат не может быть меньше минимального. Пожалуйста, введите корректное число.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите максимальное количество комнат цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(rooms_max=rooms_max)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    reply_markup = create_back_menu_keyboard("back_to_rooms_min_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите минимальный этаж (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_floor_min)


@router.message(SearchApartment.waiting_for_floor_min, F.text)
async def search_floor_min_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода минимального этажа."""
    try:
        floor_min = int(message.text)
        if floor_min < 0:
            error_msg = await message.reply(
                "Минимальный этаж не может быть отрицательным. Пожалуйста, введите корректное число.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите минимальный этаж цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(floor_min=floor_min)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    reply_markup = create_back_menu_keyboard("back_to_rooms_max_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите максимальный этаж (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_floor_max)


@router.message(SearchApartment.waiting_for_floor_max, F.text)
async def search_floor_max_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода максимального этажа."""
    try:
        floor_max = int(message.text)
        floor_min = (await state.get_data()).get("floor_min", 0)

        if floor_max < 0:
            error_msg = await message.reply(
                "Максимальный этаж не может быть отрицательным. Пожалуйста, введите корректное число.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

        if floor_max != 0 and floor_max < floor_min:
            error_msg = await message.reply(
                "Максимальный этаж не может быть меньше минимального. Пожалуйста, введите корректное число.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            return

    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите максимальный этаж цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    await state.update_data(floor_max=floor_max)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    await show_search_confirmation(message.chat.id, (await state.get_data()).get("start_message_id"), await state.get_data(), bot, state)
    await state.set_state(SearchApartment.confirm_search)


async def show_search_confirmation(chat_id: int, message_id: int, data: dict, bot: Bot, state: FSMContext):
    """Отображает параметры поиска и кнопку подтверждения."""
    city = data.get('city', 'Любой')
    price_min = data.get('price_min', 0)
    price_max = data.get('price_max', 0)
    rooms_min = data.get('rooms_min', 0)
    rooms_max = data.get('rooms_max', 0)
    floor_min = data.get('floor_min', 0)
    floor_max = data.get('floor_max', 0)

    text = "Параметры поиска:\n" \
           f"Город: {city}\n" \
           f"Цена: от {price_min} до {price_max if price_max != 0 else 'не ограничено'}\n" \
           f"Комнаты: от {rooms_min} до {rooms_max if rooms_max != 0 else 'не ограничено'}\n" \
           f"Этаж: от {floor_min} до {floor_max if floor_max != 0 else 'не ограничено'}\n\n" \
           "Подтвердить поиск?"

    keyboard = [
        [InlineKeyboardButton(text="Подтвердить", callback_data="search_confirm")],
        [InlineKeyboardButton(text="Редактировать", callback_data="search_edit")],
        [InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)
    await state.set_state(SearchApartment.confirm_search)



@router.callback_query(SearchApartment.confirm_search, F.data == "search_confirm")
async def confirm_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик подтверждения параметров поиска."""
    await callback_query.answer()
    data = await state.get_data()
    city = data.get('city', '')
    price_min = data.get('price_min', 0)
    price_max = data.get('price_max', 0)
    rooms_min = data.get('rooms_min', 0)
    rooms_max = data.get('rooms_max', 0)
    floor_min = data.get('floor_min', 0)
    floor_max = data.get('floor_max', 0)

    apartments = fetch_apartments(
        city=city.upper().strip(),
        price_min=price_min,
        price_max=price_max,
        rooms_min=rooms_min,
        rooms_max=rooms_max,
        floor_min=floor_min,
        floor_max=floor_max
    )
    if apartments:
        await state.update_data(apartments=apartments)
        start_message_id = (await state.get_data()).get("start_message_id")

        try:
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=start_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

        # Передаем chat_id и message_id
        await send_apartment(callback_query.message.chat.id, apartments, 0, state, bot)
        await state.set_state(SearchApartment.showing_results)  # Устанавливаем состояние показа результатов
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Квартиры не найдены.",
                                reply_markup=create_main_menu_keyboard())
        await delete_message(bot, callback_query.message.chat.id, callback_query.message.message_id)
        await state.clear()


@router.callback_query(SearchApartment.confirm_search, F.data == "search_edit")
async def edit_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик запроса на редактирование параметров поиска."""
    await callback_query.answer()
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите город для поиска:",
    )
    await state.set_state(SearchApartment.waiting_for_city)


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к началу поиска квартиры."""
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите город для поиска:",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_city)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_price_min_search")
async def back_to_price_min_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к вводу минимальной цены."""

    reply_markup = create_back_menu_keyboard("back_to_city_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите минимальную цену (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )
    await state.set_state(SearchApartment.waiting_for_price_min)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_city_search")
async def back_to_city_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к вводу города."""
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите город для поиска:",
        reply_markup=reply_markup,
    )

    await state.set_state(SearchApartment.waiting_for_city)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_price_max_search")
async def back_to_price_max_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к вводу максимальной цены."""

    reply_markup = create_back_menu_keyboard("back_to_price_min_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите максимальную цену (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )
    await state.set_state(SearchApartment.waiting_for_price_max)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_rooms_min_search")
async def back_to_rooms_min_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к вводу минимального количества комнат."""

    reply_markup = create_back_menu_keyboard("back_to_price_max_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите минимальное количество комнат (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )
    await state.set_state(SearchApartment.waiting_for_rooms_min)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_rooms_max_search")
async def back_to_rooms_max_search(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к вводу максимального количества комнат."""

    reply_markup = create_back_menu_keyboard("back_to_rooms_min_search")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите максимальное количество комнат (или 0, если нет ограничений):",
        reply_markup=reply_markup,
    )
    await state.set_state(SearchApartment.waiting_for_rooms_max)
    await callback_query.answer()

@router.callback_query(SearchApartment.showing_results, F.data.startswith("get_user_")) # Обновил startswith для соответствия callback.data
async def handle_get_user(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot): # Переименовал функцию для соответствия traceback
    await callback_query.answer()

    parts = callback_query.data.split("_")
    index_str = parts[-1]  # Берем последний элемент списка parts
    apartment_index = int(index_str)

    data = await state.get_data()
    apartments = data.get('apartments')

    if apartments and 0 <= apartment_index < len(apartments):
        apartment = apartments[apartment_index]
        user_id = apartment.get('username') #  В вашем примере данных ключ 'username', а не 'user_id'

        if user_id:
            await callback_query.message.answer(
                f"Контакт пользователя: @{user_id}",
                parse_mode=ParseMode.HTML
            )
        else:
            await callback_query.message.answer("Информация о пользователе не найдена.")
    else:
        await callback_query.message.answer("Произошла ошибка при обработке запроса.")