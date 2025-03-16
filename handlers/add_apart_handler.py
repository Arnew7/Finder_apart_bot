import re

from aiogram import Router, types, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, callback_query
from Database import insert_apartment
from Utilites import delete_message, delayed_delete, create_balcony_keyboard, create_renovation_keyboard, \
    create_building_year_keyboard, create_lift_keyboard, create_parking_keyboard, create_window_view_keyboard, \
    create_prepayment_keyboard, create_back_menu_keyboard, create_confirmation_keyboard
import asyncio

router = Router()


class AddApartment(StatesGroup):
    waiting_for_city = State()
    waiting_for_district = State()
    waiting_for_street = State()
    waiting_for_house = State()
    waiting_for_entrance = State()
    waiting_for_apartment_number = State()
    waiting_for_room = State()
    waiting_for_floor = State()
    waiting_for_total_floors = State()  # Перемещено сюда
    waiting_for_price = State()
    waiting_for_deposit = State()
    waiting_for_total_area = State()
    waiting_for_ceiling_height = State()
    waiting_for_bathroom = State()
    waiting_for_balcony = State()
    waiting_for_renovation = State()
    waiting_for_window_view = State()
    waiting_for_building_year = State()
    waiting_for_lift = State()
    waiting_for_parking = State()
    waiting_for_prepayment = State()
    confirmation = State()
    message_id = State()







@router.callback_query(F.data == "add")
async def add_apartment_start(
    callback_query: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """Начало добавления квартиры."""
    await state.clear() # очистка данных предыдущего заполнения
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    # Получение username из сообщения пользователя
    username = callback_query.from_user.username
    await state.update_data(username=username)

    # Удаляем сообщение с главным меню
    await delete_message(bot, callback_query.message.chat.id, callback_query.message.message_id)

    msg = await bot.send_message(callback_query.message.chat.id, "Укажите город:", reply_markup=reply_markup)
    await state.update_data(start_message_id=msg.message_id)

    await state.set_state(AddApartment.waiting_for_city)

    await callback_query.answer()


@router.message(AddApartment.waiting_for_city, F.text)
async def city_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода города."""
    city = message.text.strip()
    if not re.match(r"^[а-яА-ЯёЁ\s-]+$", city):
        error_msg = await message.reply(
            "Пожалуйста, используйте только русские буквы, пробелы и дефисы.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    if len(city) > 50:
        error_msg = await message.reply(
            "Слишком длинное название города. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(city) < 2:
        error_msg = await message.reply(
            "Слишком короткое название города. Пожалуйста, введите длиннее.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(city=city.upper())
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_add")  # Кнопка "Назад" ведет к началу добавления
    start_message_id = (await state.get_data()).get("start_message_id")
    try:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=start_message_id, # edit стартового сообщения
            text="Укажите район:",
            reply_markup=reply_markup,
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")

    await state.set_state(AddApartment.waiting_for_district)


@router.message(AddApartment.waiting_for_district, F.text)
async def district_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода района."""
    district = message.text.strip()
    if not re.match(r"^[а-яА-ЯёЁ\s-]+$", district):
        error_msg = await message.reply(
            "Пожалуйста, используйте только русские буквы, пробелы и дефисы.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    if len(district) > 50:
        error_msg = await message.reply(
            "Слишком длинное название района. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(district) < 2:
        error_msg = await message.reply(
            "Слишком короткое название района. Пожалуйста, введите длиннее.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(district=district.upper())
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_city")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите улицу:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_street)


@router.message(AddApartment.waiting_for_street, F.text)
async def street_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода улицы."""
    street = message.text.strip()
    if not re.match(r"^[а-яА-ЯёЁ\s\d.,-]+$", street):
        error_msg = await message.reply(
            "Пожалуйста, используйте только русские буквы, цифры, пробелы и знаки препинания.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    if len(street) > 50:
        error_msg = await message.reply(
            "Слишком длинное название улицы. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(street) < 2:
        error_msg = await message.reply(
            "Слишком короткое название улицы. Пожалуйста, введите длиннее.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(street=street.lower())
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_district")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите номер дома:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_house)


@router.message(AddApartment.waiting_for_house, F.text)
async def house_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода номера дома."""
    house = message.text.strip()
    if not house.isdigit():
        error_msg = await message.reply(
            "Номер дома должен быть числом. Пожалуйста, введите корректный номер дома.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(house) > 4:
        error_msg = await message.reply(
            "Слишком длинный номер дома. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(house=house)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_street")
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите номер подъезда:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_entrance)


@router.callback_query(F.data == "back_to_house")
async def back_to_house(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    start_message_id = (await state.get_data()).get("start_message_id")
    reply_markup = create_back_menu_keyboard("back_to_street")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите номер дома:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_house)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_street")
async def back_to_street(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    start_message_id = (await state.get_data()).get("start_message_id")
    reply_markup = create_back_menu_keyboard("back_to_district")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите улицу:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_street)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_district")
async def back_to_district(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    start_message_id = (await state.get_data()).get("start_message_id")
    reply_markup = create_back_menu_keyboard("back_to_add")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите район:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_district)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_city")
async def back_to_city(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    start_message_id = (await state.get_data()).get("start_message_id")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=start_message_id,
        text="Укажите город:",
        reply_markup=reply_markup,
    )

    await state.set_state(AddApartment.waiting_for_city)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_add")
async def back_to_add(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к началу добавления квартиры."""
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    start_message = await callback_query.message.answer("Укажите город:", reply_markup=reply_markup)

    username = callback_query.from_user.username
    await state.update_data(username=username, start_message_id=start_message.message_id)

    await state.set_state(AddApartment.waiting_for_city)

    await callback_query.answer()


@router.message(AddApartment.waiting_for_apartment_number, F.text)
async def apartment_number_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода номера квартиры."""
    apartment_number = message.text.strip()
    if not apartment_number.isdigit():
        error_msg = await message.reply(
            "Номер квартиры должен быть числом. Пожалуйста, введите корректный номер квартиры.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(apartment_number) > 3:
        error_msg = await message.reply("Слишком длинный номер квартиры. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(apartment_number=apartment_number)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_apartment_number")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите количество комнат:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_room)


@router.message(AddApartment.waiting_for_entrance, F.text)
async def entrance_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода номера подъезда."""
    entrance = message.text.strip()
    if not entrance.isdigit():
        error_msg = await message.reply(
            "Номер подъезда должен быть числом. Пожалуйста, введите корректный номер подъезда.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(entrance) > 2:
        error_msg = await message.reply("Слишком длинный номер подъезда. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return

    await state.update_data(entrance=entrance)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_entrance")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите номер квартиры:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_apartment_number)



@router.message(AddApartment.waiting_for_apartment_number, F.text)
async def apartment_number_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода номера квартиры."""
    apartment_number = message.text.strip()
    if not apartment_number.isdigit():
        error_msg = await message.reply(
            "Номер квартиры должен быть числом. Пожалуйста, введите корректный номер квартиры.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    elif len(apartment_number) > 3:
        error_msg = await message.reply("Слишком длинный номер квартиры. Пожалуйста, введите короче.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(apartment_number=apartment_number)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_apartment_number")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите количество комнат:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_room)


@router.message(AddApartment.waiting_for_room, F.text)
async def room_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода количества комнат."""
    try:
        rooms = int(message.text)
        if rooms <= 0 or rooms > 10:
            error_msg = await message.reply("Неадекватное количество комнат. Пожалуйста, введите число от 1 до 10.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите число комнат цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(room=rooms)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_room")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите этаж:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_floor)


@router.message(AddApartment.waiting_for_floor, F.text)
async def floor_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода этажа квартиры."""
    try:
        floor = int(message.text)
        if floor <= 0 or floor > 300:
            error_msg = await message.reply("Неадекватное количество этажей. Пожалуйста, введите число от 1 до 300.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return

    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите этаж цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return

    await state.update_data(floor=floor)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_floor")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите этажность дома:",
        reply_markup=reply_markup,
    )
    await state.set_state(AddApartment.waiting_for_total_floors)


@router.message(AddApartment.waiting_for_total_floors, F.text)
async def total_floors_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода этажности дома."""
    try:
        total_floors = int(message.text)
        floor = (await state.get_data()).get('floor')  # Получаем этаж квартиры
        if total_floors <= 0 or total_floors > 300:
            error_msg = await message.reply("Неадекватная этажность. Пожалуйста, введите реальную этажность.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return

        if floor > total_floors:
            error_msg = await message.reply(
                f"Этаж квартиры ({floor}) не может быть больше этажности дома ({total_floors}). "
                f"Пожалуйста, введите корректную этажность дома."
            )
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return

    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите этажность цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return

    await state.update_data(total_floors=total_floors)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_total_floors")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите ежемесячную цену аренды:",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_price)


@router.message(AddApartment.waiting_for_price, F.text)
async def price_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода ежемесячной цены аренды."""
    try:
        price = float(message.text)
        if price <= 0 or price > 1000000:
            error_msg = await message.reply("Неадекватная цена. Пожалуйста, введите реальную цену.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите цену цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(price=price)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_price")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите залог:",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_deposit)


@router.message(AddApartment.waiting_for_deposit, F.text)
async def deposit_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода залога."""
    try:
        deposit = float(message.text)
        if deposit < 0 or deposit > 1000000:
            error_msg = await message.reply("Неадекватный залог. Пожалуйста, введите реальную сумму.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите залог цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(deposit=deposit)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_deposit")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите общую площадь:",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_total_area)


@router.message(AddApartment.waiting_for_total_area, F.text)
async def total_area_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода общей площади."""
    try:
        total_area = float(message.text)
        if total_area <= 2 or total_area > 1000:
            error_msg = await message.reply("Неадекватная площадь. Пожалуйста, введите реальную площадь.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите площадь цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(total_area=total_area)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_back_menu_keyboard("back_to_total_area")  # Используем функцию для создания клавиатуры
    start_message_id = (await state.get_data()).get("start_message_id") # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id,
        text="Укажите высоту потолков:",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_ceiling_height)


@router.message(AddApartment.waiting_for_ceiling_height, F.text)
async def ceiling_height_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода высоты потолков."""
    try:
        ceiling_height = float(message.text)
        if ceiling_height < 2 or ceiling_height > 5:
            error_msg = await message.reply("Неадекватная высота потолков. Пожалуйста, введите реальную высоту.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите высоту потолков цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return

    await state.update_data(ceiling_height=ceiling_height)
    await delete_message(bot, message.chat.id, message.message_id)

    keyboard = [
        [InlineKeyboardButton(text="Раздельный", callback_data="bathroom_yes"),
         InlineKeyboardButton(text="Совмещенный", callback_data="bathroom_no")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_ceiling_height"),
         InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    start_message_id = (await state.get_data()).get('start_message_id')  # Получаем id сообщения для редактирования
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=start_message_id, # Используем сохраненный message_id
        text="Санузел раздельный?",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_bathroom)



@router.callback_query(AddApartment.waiting_for_bathroom, F.data.in_({"bathroom_yes", "bathroom_no"}))
async def bathroom_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора наличия санузла."""
    bathroom = callback_query.data == "bathroom_yes"
    await state.update_data(bathroom=bathroom)

    reply_markup = create_balcony_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Есть балкон/лоджия?",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_balcony)
    await callback_query.answer()



@router.callback_query(AddApartment.waiting_for_balcony, F.data.in_({"balcony_yes", "balcony_no"}))
async def balcony_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора наличия балкона/лоджии."""
    balcony = callback_query.data == "balcony_yes"
    await state.update_data(balcony=balcony)

    reply_markup = create_renovation_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Требуется ремонт?",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_renovation)
    await callback_query.answer()




@router.callback_query(AddApartment.waiting_for_renovation, F.data.in_({"renovation_yes", "renovation_no"}))
async def renovation_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора необходимости ремонта."""
    renovation = callback_query.data == "renovation_yes"
    await state.update_data(renovation=renovation)

    reply_markup = create_window_view_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Вид из окна во двор?",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_window_view)
    await callback_query.answer()




@router.callback_query(AddApartment.waiting_for_window_view, F.data.in_({"view_yard", "view_street"}))
async def window_view_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора вида из окна."""
    window_view = callback_query.data == "view_yard"
    await state.update_data(window_view=window_view)

    reply_markup = create_building_year_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Укажите год постройки:",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_building_year)
    await callback_query.answer()



@router.message(AddApartment.waiting_for_building_year, F.text)
async def building_year_entered(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода года постройки."""
    try:
        building_year = int(message.text)
        if building_year < 1800 or building_year > 2025:
            error_msg = await message.reply("Неадекватный год постройки. Пожалуйста, введите реальный год.")
            asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
            await delete_message(bot, message.chat.id, message.message_id)
            return
    except ValueError:
        error_msg = await message.reply("Пожалуйста, введите год постройки цифрами.")
        asyncio.create_task(delayed_delete(bot, message.chat.id, error_msg.message_id))
        await delete_message(bot, message.chat.id, message.message_id)
        return
    await state.update_data(building_year=building_year)
    await delete_message(bot, message.chat.id, message.message_id)

    reply_markup = create_lift_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=message.chat.id, message_id=start_message_id, text="Есть лифт?", reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_lift)



@router.callback_query(AddApartment.waiting_for_lift, F.data.in_({"lift_yes", "lift_no"}))
async def lift_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора наличия лифта."""
    lift = callback_query.data == "lift_yes"
    await state.update_data(lift=lift)

    reply_markup = create_parking_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Есть парковка?", reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_parking)
    await callback_query.answer()


@router.callback_query(AddApartment.waiting_for_parking, F.data.in_({"parking_yes", "parking_no"}))
async def parking_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора наличия парковки."""
    parking = callback_query.data == "parking_yes"
    await state.update_data(parking=parking)

    reply_markup = create_prepayment_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Требуется ли предоплата?",
        reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_prepayment)
    await callback_query.answer()



@router.callback_query(AddApartment.waiting_for_prepayment, F.data.in_({"prepayment_yes", "prepayment_no"}))
async def prepayment_chosen(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработка выбора необходимости предоплаты."""
    prepayment = callback_query.data == "prepayment_yes"
    await state.update_data(prepayment=prepayment)
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await show_confirmation(callback_query.message.chat.id, start_message_id, data, bot, state)
    await state.set_state(AddApartment.confirmation)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_lift")
async def back_to_lift(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Возврат к выбору наличия лифта."""

    reply_markup = create_lift_keyboard()
    data = await state.get_data()
    start_message_id = data.get('start_message_id')
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id, message_id=start_message_id, text="Есть лифт?", reply_markup=reply_markup
    )
    await state.set_state(AddApartment.waiting_for_lift)
    await callback_query.answer()


async def show_confirmation(chat_id: int, message_id: int, data: dict, bot: Bot, state: FSMContext):
    """Отображает сообщение с подтверждением и собранными данными."""

    # Format apartment details for confirmation message
    text = "Пожалуйста, подтвердите данные:\n" \
           f"Город: {data.get('city', 'Не указано')}\n" \
           f"Район: {data.get('district', 'Не указано')}\n" \
           f"Улица: {data.get('street', 'Не указано')}\n" \
           f"Номер дома: {data.get('house', 'Не указано')}\n" \
           f"Подъезд: {data.get('entrance', 'Не указано')}\n" \
           f"Номер квартиры: {data.get('apartment_number', 'Не указано')}\n" \
           f"Комнат: {data.get('room', 'Не указано')}\n" \
           f"Этаж: {data.get('floor', 'Не указано')}\n" \
           f"Этажность дома: {data.get('total_floors', 'Не указано')}\n" \
           f"Цена аренды: {data.get('price', 'Не указано')}\n" \
           f"Залог: {data.get('deposit', 'Не указано')}\n" \
           f"Общая площадь: {data.get('total_area', 'Не указано')}\n" \
           f"Высота потолков: {data.get('ceiling_height', 'Не указано')}\n" \
           f"Санузел раздельный: {'Да' if data.get('bathroom') else 'Нет'}\n" \
           f"Балкон/лоджия: {'Есть' if data.get('balcony') else 'Нет'}\n" \
           f"Требуется ремонт: {'Да' if data.get('renovation') else 'Нет'}\n" \
           f"Вид из окон во двор: {'Да' if data.get('window_view') else 'Нет'}\n" \
           f"Год постройки: {data.get('building_year', 'Не указано')}\n" \
           f"Лифт: {'Есть' if data.get('lift') else 'Нет'}\n" \
           f"Парковка: {'Есть' if data.get('parking') else 'Нет'}\n" \
           f"Предоплата: {'Да' if data.get('prepayment') else 'Нет'}\n"

    reply_markup = create_confirmation_keyboard()
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)
    await state.set_state(AddApartment.confirmation)




@router.callback_query(AddApartment.confirmation, F.data == "confirm")
async def confirm_data(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик подтверждения данных квартиры."""
    data = await state.get_data()
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    username = callback_query.from_user.username
    await complete_apartment_creation(chat_id, message_id, data, bot, username)
    await state.clear()
    await callback_query.answer("Данные сохранены!")


@router.callback_query(AddApartment.confirmation, F.data == "edit")
async def edit_data(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик запроса на редактирование данных квартиры."""

    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Пожалуйста, укажите город:",
    )
    await state.set_state(AddApartment.waiting_for_city)  # Возврат в начало
    username = callback_query.from_user.username
    await callback_query.answer("Начните ввод заново")


async def complete_apartment_creation(chat_id: int, message_id: int, data: dict, bot: Bot, username: str):
    """Завершает процесс создания квартиры и сохраняет данные."""

    apartment_data = {
        'username': username,
        'city': data.get('city', 'Не указано'),
        'district': data.get('district', 'Не указано'),
        'street': data.get('street', 'Не указано'),
        'house': data.get('house', 'Не указано'),
        'entrance': data.get('entrance', 'Не указано'),
        'apartment_number': data.get('apartment_number', 'Не указано'),
        'room': data.get('room', 'Не указано'),
        'floor': data.get('floor', 'Не указано'),
        'total_floors': data.get('total_floors', 'Не указано'),
        'price': data.get('price', 'Не указано'),
        'deposit': data.get('deposit', 'Не указано'),
        'total_area': data.get('total_area', 'Не указано'),
        'ceiling_height': data.get('ceiling_height', 'Не указано'),
        'bathroom': data.get('bathroom', False),
        'balcony': data.get('balcony', False),
        'renovation': data.get('renovation', False),
        'window_view': data.get('window_view', False),
        'building_year': data.get('building_year', 'Не указано'),
        'lift': data.get('lift', False),
        'parking': data.get('parking', False),
        'prepayment': data.get('prepayment', False),
    }

    # Insert the apartment data into the database
    insert_apartment(apartment_data, username)

    # Format apartment details for display
    text = "Квартира добавлена!\n" \
           f"Город: {apartment_data['city']}\n" \
           f"Район: {apartment_data['district']}\n" \
           f"Улица: {apartment_data['street']}\n" \
           f"Номер дома: {apartment_data['house']}\n" \
           f"Подъезд: {apartment_data['entrance']}\n" \
           f"Номер квартиры: {apartment_data['apartment_number']}\n" \
           f"Комнат: {apartment_data['room']}\n" \
           f"Этаж: {apartment_data['floor']}\n" \
           f"Этажность дома: {apartment_data['total_floors']}\n" \
           f"Цена аренды: {apartment_data['price']}\n" \
           f"Залог: {apartment_data['deposit']}\n" \
           f"Общая площадь: {apartment_data['total_area']}\n" \
           f"Высота потолков: {apartment_data['ceiling_height']}\n" \
           f"Санузел раздельный: {'Да' if apartment_data['bathroom'] else 'Нет'}\n" \
           f"Балкон/лоджия: {'Есть' if apartment_data['balcony'] else 'Нет'}\n" \
           f"Требуется ремонт: {'Да' if apartment_data['renovation'] else 'Нет'}\n" \
           f"Вид из окон во двор: {'Да' if apartment_data['window_view'] else 'Нет'}\n" \
           f"Год постройки: {apartment_data['building_year']}\n" \
           f"Лифт: {'Есть' if apartment_data['lift'] else 'Нет'}\n" \
           f"Парковка: {'Есть' if apartment_data['parking'] else 'Нет'}\n" \
           f"Предоплата: {'Да' if apartment_data['prepayment'] else 'Нет'}\n"

    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup)

