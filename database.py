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
                is_available BOOLEAN NOT NULL DEFAULT 1,
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
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
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
                SELECT b.id, u.name, h.name, r.category, b.check_in_date, b.check_out_date, b.status
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
                SELECT id, category, price
                FROM rooms
                WHERE hotel_id = ? AND is_available = 1
            """, (hotel_id,))
            return cursor.fetchall()

    def book_room(self, user_id, room_id, check_in_date, check_out_date):
        # Check if the room is available for the requested dates
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_available FROM rooms WHERE id = ?
            """, (room_id,))
            room = cursor.fetchone()
            if room and room[0] == 1:
                cursor.execute("""
                    INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (user_id, room_id, check_in_date, check_out_date))
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

