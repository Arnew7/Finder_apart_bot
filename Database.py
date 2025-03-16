import logging
import sqlite3



DATABASE_URL = "apartments.db" # Укажи путь к своей базе данных

def create_connection(db_name='apartments.db'):
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

def get_username_by_apartment_id(apartment_id):
    """Получает username владельца квартиры из базы данных по ID квартиры."""
    conn = create_connection()
    cursor = conn.cursor()
    username = None
    try:
        cursor.execute("SELECT username FROM apartments WHERE id = ?", (apartment_id,))
        result = cursor.fetchone()
        if result:
            username = result[0]
    except sqlite3.Error as e:
        print(f"Ошибка при запросе username из базы данных: {e}")
    finally:
        if conn: # Добавлена проверка на существование соединения перед закрытием
            conn.close()
    return username

def fetch_apartments(city="", price_min=0, price_max=0, rooms_min=0, rooms_max=0, floor_min=0, floor_max=0):
    """Выполняет поиск квартир в базе данных."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM apartments WHERE 1=1"  # Начинаем с истины, чтобы упростить добавление условий

        params = []  # Список для параметров запроса

        if city:
            query += " AND city = ?"
            params.append(city)
        if price_min > 0:
            query += " AND price >= ?"
            params.append(price_min)
        if price_max > 0:
            query += " AND price <= ?"
            params.append(price_max)
        if rooms_min > 0:
            query += " AND room >= ?"
            params.append(rooms_min)
        if rooms_max > 0:
            query += " AND room <= ?"
            params.append(rooms_max)
        if floor_min > 0:
            query += " AND floor >= ?"
            params.append(floor_min)
        if floor_max > 0:
            query += " AND floor <= ?"
            params.append(floor_max)

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Преобразование результатов в список словарей
        column_names = [description[0] for description in cursor.description]  # Получаем имена столбцов
        apartments = [dict(zip(column_names, row)) for row in results]  # Создаем словари

        return apartments
    except sqlite3.Error as e:
        print(f"Error fetching apartments: {e}")
        return []  # Вернуть пустой список в случае ошибки
    finally:
        conn.close()



def delete_apartment(apartment_id: int, username: str) -> bool:
    """Deletes an apartment from the database by ID, only if the user owns it."""
    conn = create_connection()
    cursor = conn.cursor()
    try:

        cursor.execute(
            "DELETE FROM apartments WHERE id = ? AND username = ?",
            (apartment_id, username),
        )
        conn.commit()
        rowcount = cursor.rowcount

        if rowcount > 0:

            return True
        else:

            return False
    except sqlite3.Error as e:

        return False
    finally:
        if conn:
            conn.close()


def get_user_apartments(username: int) -> list:
    """Retrieves all apartments listed by a specific user."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM apartments WHERE username = ?", (username,))
        apartments = cursor.fetchall()
        return apartments
    except sqlite3.Error as e:
        print(f"Error fetching user apartments: {e}")
        return []
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
