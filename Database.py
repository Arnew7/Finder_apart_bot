import sqlite3

DATABASE_URL = "apartments.db" # Укажи путь к своей базе данных

def create_connection():
    return sqlite3.connect(DATABASE_URL)

def create_connection(db_name='apartments_db.db'):
    """Создает соединение с базой данных SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,  -- Добавлено поле username
                city TEXT,
                district TEXT,
                street TEXT,
                house TEXT,
                entrance TEXT,
                apartment_number TEXT,
                room TEXT,
                floor TEXT,
                total_floors TEXT,
                price REAL,
                deposit REAL,
                total_area REAL,
                ceiling_height REAL,
                bathroom INTEGER,
                balcony INTEGER,
                renovation INTEGER,
                window_view TEXT,
                building_year TEXT,
                lift INTEGER,
                parking INTEGER,
                prepayment INTEGER
            )
        """)
        conn.commit()
        print("Table 'apartments' created or already exists.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def insert_apartment(data, username): # Изменено: добавлен параметр username
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO apartments (
                username, city, district, street, house, entrance, apartment_number,
                room, floor, total_floors, price, deposit, total_area,
                ceiling_height, bathroom, balcony, renovation, window_view,
                building_year, lift, parking, prepayment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, # Добавлено значение username
            data.get('city', 'Не указано'),
            data.get('district', 'Не указано'),
            data.get('street', 'Не указано'),
            data.get('house', 'Не указано'),
            data.get('entrance', 'Не указано'),
            data.get('apartment_number', 'Не указано'),
            data.get('room', 'Не указано'),
            data.get('floor', 'Не указано'),
            data.get('total_floors', 'Не указано'),
            data.get('price', 'Не указано'),
            data.get('deposit', 'Не указано'),
            data.get('total_area', 'Не указано'),
            data.get('ceiling_height', 'Не указано'),
            1 if data.get('bathroom', False) else 0,
            1 if data.get('balcony', False) else 0,
            1 if data.get('renovation', False) else 0,
            data.get('window_view', 'Не указано'),
            data.get('building_year', 'Не указано'),
            1 if data.get('lift', False) else 0,
            1 if data.get('parking', False) else 0,
            1 if data.get('prepayment', False) else 0
        ))
        conn.commit()
        print(f"Apartment added successfully for user: {username}")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()



def find_apartments(filters=None):
    """
    Находит квартиры, соответствующие заданным фильтрам.

    Args:
        filters (dict, optional): Словарь с фильтрами. Ключи - названия столбцов, значения - значения для фильтрации.
                                     Например: {'property_type': 'Квартира', 'price': (100000, 200000)}  # Цена в диапазоне

    Returns:
        list: Список словарей, представляющих найденные квартиры.  Вернет пустой список, если ничего не найдено.
    """
    conn = create_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM apartments"
    params = []
    where_clauses = []

    if filters:
        for column, value in filters.items():
            if isinstance(value, tuple):  # Для диапазонов (например, цен)
                where_clauses.append(f"{column} BETWEEN ? AND ?")
                params.extend(value)
            else:
                where_clauses.append(f"{column} = ?")
                params.append(value)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Преобразование результатов в список словарей
    results = []
    column_names = [description[0] for description in cursor.description]  # Получаем имена столбцов
    for row in rows:
        results.append(dict(zip(column_names, row)))

    return results



def delete_apartment(apartment_id):
    """Удаляет квартиру из базы данных по ID."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM apartments WHERE id = ?", (apartment_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Apartment with ID {apartment_id} deleted successfully.")
        else:
            print(f"Apartment with ID {apartment_id} not found.")
    except sqlite3.Error as e:
        print(f"Error deleting apartment: {e}")
    finally:
        conn.close()



def get_all_apartments():
    """Выводит все квартиры из базы данных и возвращает их в виде списка словарей."""
    conn = create_connection()
    cursor = conn.cursor()
    apartments_list = []
    try:
        cursor.execute("SELECT * FROM apartments")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description] # Получаем имена столбцов

        if rows:
            for row in rows:
                apartment_dict = {}
                for i, col_name in enumerate(column_names):
                    apartment_dict[col_name] = row[i]
                apartments_list.append(apartment_dict)
        else:
            print("No apartments found in the database.") # This print statement is for debugging in this function itself. In the bot, handle empty list appropriately.

    except sqlite3.Error as e:
        print(f"Error fetching apartments: {e}")
    finally:
        conn.close()
    return apartments_list

if __name__ == '__main__':
    create_table() # Ensure table exists before fetching data
    all_apartments = get_all_apartments()

    if all_apartments:
        print("\n--- All Apartments ---")
        for apartment in all_apartments:
            print(f"ID: {apartment.get('id', 'N/A')}, Username: {apartment.get('username', 'N/A')}, "
                  f"City: {apartment.get('city', 'N/A')}, District: {apartment.get('district', 'N/A')}, "
                  f"Street: {apartment.get('street', 'N/A')}, House: {apartment.get('house', 'N/A')}, "
                  f"Apartment Number: {apartment.get('apartment_number', 'N/A')}, "
                  f"Room: {apartment.get('room', 'N/A')}, Floor: {apartment.get('floor', 'N/A')}, "
                  f"Total Floors: {apartment.get('total_floors', 'N/A')}, Price: {apartment.get('price', 'N/A')}, "
                  f"Total Area: {apartment.get('total_area', 'N/A')}, Ceiling Height: {apartment.get('ceiling_height', 'N/A')}, "
                  f"Balcony: {apartment.get('balcony', 'N/A')}, Window View: {apartment.get('window_view', 'N/A')}, "
                  f"building_year: {apartment.get('building_year', 'N/A')}, lift: {apartment.get('lift', 'N/A')}, "
                  f"parking: {apartment.get('parking', 'N/A')}, prepayment: {apartment.get('prepayment', 'N/A')}, ",)

if __name__ == '__main__':
    create_table()  # Создаем таблицу, если она не существует



    # Пример поиска квартир по фильтрам
    search_filters = {'property_type': 'Квартира', 'price': (100000, 200000)}
    found_apartments = find_apartments(search_filters)
    print("Найденные квартиры:")
    for apartment in found_apartments:
        print(apartment)

    # Пример удаления квартиры
    apartment_id_to_delete = 1  # Предполагаем, что у нас есть квартира с ID 1
    if delete_apartment(apartment_id_to_delete):
        print(f"Квартира с ID {apartment_id_to_delete} успешно удалена.")
    else:
        print(f"Квартира с ID {apartment_id_to_delete} не найдена.")

    # Пример получения всех квартир
    all_apartments = get_all_apartments()
    print("\nВсе квартиры:")
    for apartment in all_apartments:
        print(apartment)