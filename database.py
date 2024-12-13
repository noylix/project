import sqlite3

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('customer', 'admin'))
            )
            """)
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                rating INTEGER,
                country TEXT
            )
            """)
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_id INTEGER NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('Люкс', 'Полулюкс', 'Стандарт')),
                capacity INTEGER NOT NULL,
                price REAL NOT NULL,
                is_available BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (hotel_id) REFERENCES hotels (id)
            )
            """)
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                booking_time TEXT DEFAULT (DATETIME('now')),
                status TEXT NOT NULL DEFAULT 'в ожидании',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
            """)
            # Вставка данных в таблицу hotels
            cursor.execute("""
                INSERT INTO hotels (name, description, rating, country) VALUES
                ('Отель Москва', 'Уютный отель в центре города', 5, 'Россия'),
                ('Liberty Inn', 'Отель с панорамным видом на Нью-Йорк', 4, 'США'),
                ('Paris Luxury Hotel', 'Отель в историческом центре Парижа', 5, 'Франция'),
                ('Berlin Grand Hotel', 'Отель в центре Берлина с современными удобствами', 4, 'Германия'),
                ('Roma Palace', 'Классический отель в центре Рима', 5, 'Италия'),
                ('Tokyo Bay Hotel', 'Современный отель с видом на залив в Токио', 4, 'Япония'),
                ('Beijing Great Wall Hotel', 'Отель с видом на Великую Китайскую стену', 5, 'Китай'),
                ('Toronto Towers', 'Элегантный отель в сердце Торонто', 4, 'Канада'),
                ('Madrid Sunset Hotel', 'Комфортабельный отель с видом на закат в Мадриде', 4, 'Испания'),
                ('London Regency Hotel', 'Роскошный отель в центре Лондона', 5, 'Великобритания')
            """)

            # Вставка данных в таблицу rooms (примерные данные для номеров)
            cursor.execute("""
                INSERT INTO rooms (hotel_id, category, capacity, price, is_available) VALUES
                (1, 'Люкс', 2, 10000.0, 1),
                (1, 'Полулюкс', 2, 7000.0, 1),
                (1, 'Стандарт', 1, 5000.0, 0),
                (2, 'Люкс', 3, 12000.0, 1),
                (2, 'Полулюкс', 2, 9000.0, 1),
                (2, 'Стандарт', 1, 6000.0, 1),
                (3, 'Люкс', 2, 15000.0, 1),
                (3, 'Полулюкс', 2, 11000.0, 0),
                (3, 'Стандарт', 1, 8000.0, 1),
                (4, 'Люкс', 2, 16000.0, 1),
                (4, 'Полулюкс', 2, 10000.0, 1),
                (4, 'Стандарт', 1, 6000.0, 0),
                (5, 'Люкс', 3, 13000.0, 1),
                (5, 'Полулюкс', 2, 8500.0, 1),
                (5, 'Стандарт', 1, 5500.0, 1),
                (6, 'Люкс', 2, 17000.0, 1),
                (6, 'Полулюкс', 2, 10000.0, 1),
                (6, 'Стандарт', 1, 6500.0, 0),
                (7, 'Люкс', 3, 14000.0, 1),
                (7, 'Полулюкс', 2, 9500.0, 1),
                (7, 'Стандарт', 1, 7000.0, 1),
                (8, 'Люкс', 2, 11000.0, 1),
                (8, 'Полулюкс', 2, 8000.0, 1),
                (8, 'Стандарт', 1, 5000.0, 1),
                (9, 'Люкс', 3, 12000.0, 1),
                (9, 'Полулюкс', 2, 8500.0, 1),
                (9, 'Стандарт', 1, 6000.0, 1),
                (10, 'Люкс', 2, 12500.0, 1),
                (10, 'Полулюкс', 2, 9000.0, 1),
                (10, 'Стандарт', 1, 6000.0, 1)
            """)
            # Add default admin user
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES ('Admin', 'admin1', 'admin2', 'admin')
                """)

    def check_user_credentials(self, email, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role, password FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user and user[3] == password:  # Compare plain passwords
                return user[0], user[1], user[2]
            return None

    def register_user(self, name, email, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'customer')",
                               (name, email, password))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_all_bookings(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.id, u.name, h.name, r.category, b.check_in_date, b.check_out_date, b.booking_time, b.status
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                JOIN rooms r ON b.room_id = r.id
                JOIN hotels h ON r.hotel_id = h.id
            """)
            return cursor.fetchall()

    def update_booking_status(self, booking_id, status):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE bookings
                    SET status = ?
                    WHERE id = ?
                """, (status, booking_id))
                conn.commit()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при обновлении статуса: {e}")

    def delete_booking(self, booking_id):
        try:
            # Открытие соединения с базой данных
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

                # Проверка, сколько строк было затронуто (если затронута хотя бы одна строка — удаление прошло успешно)
                if cursor.rowcount > 0:
                    conn.commit()
                    return True  # Успешно удалено
                else:
                    return False  # Запись не найдена или не удалена

        except sqlite3.Error as e:
            # Ошибка в работе с базой данных
            print(f"Ошибка базы данных: {e}")
            return False  # Не удалось удалить бронирование

    def add_hotel(self, name, country, description, rating):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                print(f"Попытка добавить отель: {name}, {country}, {description}, {rating}")

                if not name or not country:
                    raise ValueError("Поля 'name' и 'country' не могут быть пустыми.")

                if rating is not None and (not isinstance(rating, int) or not (1 <= rating <= 5)):
                    raise ValueError("Рейтинг должен быть целым числом от 1 до 5.")

                cursor.execute("""
                    INSERT INTO hotels (name, country, description, rating)
                    VALUES (?, ?, ?, ?)
                """, (name, country, description, rating))
                conn.commit()
                print("Отель успешно добавлен!")

        except ValueError as ve:
            print(f"Ошибка проверки данных: {ve}")
        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности данных: {e}")
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def get_hotels(self, country=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if country:
                cursor.execute("SELECT id, name, country, description, rating FROM hotels WHERE country = ?", (country,))
            else:
                cursor.execute("SELECT id, name, country, description, rating FROM hotels")
            return cursor.fetchall()


    def add_room(self, hotel_id, category, capacity, price):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rooms (hotel_id, category, capacity, price, is_available)
                VALUES (?, ?, ?, ?, 1)
            """, (hotel_id, category, capacity, price))
            conn.commit()

    def get_available_rooms(self, hotel_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, price, capacity
                FROM rooms
                WHERE hotel_id = ? AND is_available = 1
            """, (hotel_id,))
            return cursor.fetchall()  # возвращаем все поля (id, category, price, capacity)

    def book_room(self, user_id, room_id, check_in_date, check_out_date):
        # Check if the room is available for the requested dates
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_available, capacity FROM rooms WHERE id = ?
            """, (room_id,))
            room = cursor.fetchone()
            if room and room[0] == 1:
                cursor.execute("""
                    INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date, capacity, status)
                    VALUES (?, ?, ?, ?, ?, 'в ожидании')
                """, (user_id, room_id, check_in_date, check_out_date, room[1]))
                conn.commit()
                return True
        return False

    def get_user_bookings(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.id, h.name, r.category, b.check_in_date, b.check_out_date, b.status
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN hotels h ON r.hotel_id = h.id
                WHERE b.user_id = ?
            """, (user_id,))
            return cursor.fetchall()

    def get_rooms_for_hotel(self, hotel_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, capacity, price
                FROM rooms
                WHERE hotel_id = ?
            """, (hotel_id,))
            rooms = cursor.fetchall()
            return rooms



