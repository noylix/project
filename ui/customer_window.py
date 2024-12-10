from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QListWidget, QAbstractItemView,
                             QLabel, QHBoxLayout, QPushButton, QMessageBox, QDialog,
                             QLineEdit, QFormLayout, QComboBox, QSpinBox, QCalendarWidget)
from PyQt6.QtCore import Qt
from datetime import datetime

from unicodedata import category


class BookingDetailsDialog(QDialog):
    def __init__(self, parent, hotel_name, category):
        super().__init__(parent)
        self.setWindowTitle("Введите данные для бронирования")
        self.setModal(True)

        self.hotel_name = hotel_name
        self.category = category

        # Initialize the fields for booking details
        self.full_name = QLineEdit(self)
        self.email = QLineEdit(self)
        self.passport_number = QLineEdit(self)
        self.phone_number = QLineEdit(self)
        self.payment_method = QComboBox(self)
        self.payment_method.addItems(["Кредитная карта", "Дебетовая карта", "Прочее"])
        self.number_of_people = QSpinBox(self)
        self.number_of_people.setRange(1, 10)

        # Add date selectors for check-in and check-out
        self.check_in_calendar = QCalendarWidget(self)
        self.check_out_calendar = QCalendarWidget(self)

        # Set up the layout
        layout = QFormLayout()
        layout.addRow("ФИО", self.full_name)
        layout.addRow("Email", self.email)
        layout.addRow("Паспортные данные", self.passport_number)
        layout.addRow("Номер телефона", self.phone_number)
        layout.addRow("Способ оплаты", self.payment_method)
        layout.addRow("Количество человек", self.number_of_people)
        layout.addRow("Дата заезда", self.check_in_calendar)
        layout.addRow("Дата выезда", self.check_out_calendar)

        # Buttons for submitting or cancelling the booking
        submit_button = QPushButton("Подтвердить", self)
        submit_button.setStyleSheet("background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        submit_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена", self)
        cancel_button.setStyleSheet("background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def accept(self):
        # Check if all fields are filled
        if not self.full_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле 'ФИО' обязательно для заполнения.")
            return
        if not self.email.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле 'Email' обязательно для заполнения.")
            return
        if not self.passport_number.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле 'Паспортные данные' обязательно для заполнения.")
            return
        if not self.phone_number.text().strip():
            QMessageBox.warning(self, "Ошибка", "Поле 'Номер телефона' обязательно для заполнения.")
            return

        # Check date range validity
        check_in_date = self.check_in_calendar.selectedDate()
        check_out_date = self.check_out_calendar.selectedDate()
        if check_in_date >= check_out_date:
            QMessageBox.warning(self, "Ошибка", "Дата выезда должна быть позже даты заезда.")
            return

        # If all checks passed, proceed to accept the dialog
        super().accept()

    def get_user_details(self):
        return {
            "full_name": self.full_name.text(),
            "email": self.email.text(),
            "passport_number": self.passport_number.text(),
            "phone_number": self.phone_number.text(),
            "payment_method": self.payment_method.currentText(),
            "number_of_people": self.number_of_people.value(),
            "check_in_date": self.check_in_calendar.selectedDate().toString("yyyy-MM-dd"),
            "check_out_date": self.check_out_calendar.selectedDate().toString("yyyy-MM-dd"),
            "category": self.category
        }



class CustomerWindow(QWidget):
    def __init__(self, switch_window, db_manager, user_id):
        super().__init__()
        self.switch_window = switch_window
        self.db_manager = db_manager
        self.user_id = user_id
        self.setWindowTitle("Бронирование отелей")

        self.tabs = QTabWidget()

        self.booking_tab = QWidget()
        self.reservations_tab = QWidget()

        self.setup_booking_tab()
        self.setup_reservations_tab()

        self.tabs.addTab(self.booking_tab, "Бронирование")
        self.tabs.addTab(self.reservations_tab, "Мои бронирования")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.hotels = {}  # Will hold hotel ID to hotel name mapping
        self.rooms = {}  # Will hold room category to room ID mapping
        self.load_hotels()  # Load hotels when the window is initialized
        self.load_reservations()

    def setup_booking_tab(self):
        layout = QVBoxLayout()

        # Поле ввода для поиска отелей по названию
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск отелей:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Введите название отеля...")
        self.search_field.textChanged.connect(self.filter_hotels_by_name)
        search_layout.addWidget(self.search_field)
        layout.addLayout(search_layout)

        # Выпадающий список для фильтрации по стране
        layout.addWidget(QLabel("Выберите страну"))
        self.country_filter = QComboBox()
        self.country_filter.addItems(
            ["Все страны", "Россия", "США", "Франция", "Германия", "Италия", "Япония", "Китай", "Канада", "Испания",
             "Великобритания"])
        self.country_filter.currentTextChanged.connect(self.filter_hotels_by_country)
        layout.addWidget(self.country_filter)

        # Список отелей
        layout.addWidget(QLabel("Выберите отель"))
        self.hotel_list = QListWidget()
        self.hotel_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.hotel_list.itemClicked.connect(self.open_room_selection)
        layout.addWidget(self.hotel_list)

        # Список номеров
        layout.addWidget(QLabel("Доступные номера"))
        self.room_list = QListWidget()
        self.room_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.room_list)

        # Кнопки действий
        button_layout = QHBoxLayout()
        book_button = QPushButton("Забронировать")
        book_button.setStyleSheet(
            "background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        book_button.clicked.connect(self.show_booking_details_dialog)
        refresh_button = QPushButton("Обновить")
        refresh_button.setStyleSheet(
            "background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        refresh_button.clicked.connect(self.load_hotels)
        logout_button = QPushButton("Выйти")
        logout_button.setStyleSheet(
            "background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        logout_button.clicked.connect(lambda: self.switch_window("login"))

        button_layout.addWidget(book_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(logout_button)

        layout.addLayout(button_layout)
        self.booking_tab.setLayout(layout)


    def filter_hotels_by_name(self):
        search_text = self.search_field.text().strip().lower()
        if not search_text:
            # Если поле поиска пустое, загрузить все отели
            self.load_hotels()
            return

        filtered_hotels = []
        for name, hotel_id in self.hotels.items():
            if search_text in name.lower():
                filtered_hotels.append((hotel_id, name))

        self.hotel_list.clear()
        for hotel_id, name in filtered_hotels:
            self.hotel_list.addItem(name)

    def load_hotels(self):
        try:
            self.hotel_list.clear()
            selected_country = self.country_filter.currentText()

            # Получаем отели с учетом выбранной страны
            self.hotels_list = self.db_manager.get_hotels(
                country=selected_country if selected_country != "Все страны" else None)

            # Проверка на пустой список отелей
            if not self.hotels_list:
                print(f"Нет отелей для страны: {selected_country}")
                QMessageBox.warning(self, "Нет отелей", "Нет отелей для выбранной страны.")
                return  # Останавливаем выполнение, если нет отелей

            # Обновляем self.hotels
            self.hotels = {hotel[1]: hotel[0] for hotel in self.hotels_list}  # {название отеля: id отеля}

            # Применяем фильтрацию по названию, если текст в поле поиска был введен
            search_text = self.search_field.text().strip().lower()
            if search_text:
                self.filtered_hotels = [hotel for hotel in self.hotels_list if search_text in hotel[1].lower()]
            else:
                self.filtered_hotels = self.hotels_list

            # Обновляем список отелей
            self.update_hotel_list(self.filtered_hotels)
        except Exception as e:
            print(f"Ошибка при загрузке отелей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при загрузке отелей: {e}")

    def update_hotel_list(self, hotels):
        try:
            self.hotel_list.clear()

            for h in hotels:
                # Выводим данные отеля для диагностики
                print(f"Полученные данные отеля: {h}")

                # Проверяем, что данные отеля содержат 5 элементов
                if len(h) != 5:
                    print(f"Ошибка данных отеля: {h} — количество элементов не равно 5")
                    continue  # Пропускаем некорректные данные

                h_id, name, country, desc, rating = h
                self.hotel_list.addItem(f"{name} ({country}, рейтинг: {rating})")
        except Exception as e:
            print(f"Ошибка при обновлении списка отелей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении списка отелей: {e}")

    def display_hotels(self, hotels):
        self.hotel_list.clear()
        for h in hotels:
            h_id, name, country, desc, rating = h
            self.hotel_list.addItem(f"{name} ({country}, рейтинг: {rating})")

    def filter_hotels_by_country(self):
        # Когда меняется страна, обновляем список отелей
        self.load_hotels()

    def setup_reservations_tab(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ваши бронирования"))
        self.booking_list = QListWidget()
        self.booking_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.booking_list)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Отменить бронь")
        cancel_button.setStyleSheet("background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        cancel_button.clicked.connect(self.cancel_reservation)
        refresh_button = QPushButton("Обновить")
        refresh_button.setStyleSheet("background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        refresh_button.clicked.connect(self.load_reservations)
        logout_button = QPushButton("Выйти")
        logout_button.setStyleSheet("background-color: #0066CC; color: white; padding: 10px; border-radius: 5px; font-size: 14px;")
        logout_button.clicked.connect(lambda: self.switch_window("login"))

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(logout_button)

        layout.addLayout(button_layout)
        self.reservations_tab.setLayout(layout)


    def open_room_selection(self, item):
        hotel_name = item.text().split("(")[0].strip()  # Extract hotel name
        hotel_id = self.hotels.get(hotel_name)
        if hotel_id:
            self.load_rooms(hotel_id)

    def load_rooms(self, hotel_id):
        self.room_list.clear()
        rooms = self.db_manager.get_available_rooms(hotel_id)
        self.rooms = {}  # Reset rooms mapping
        for r in rooms:
            r_id, category, price = r  # Изменим с номера на категорию
            self.rooms[category] = r_id  # Map room category to room ID
            self.room_list.addItem(f"Номер {category} | Цена: {price} руб.")  # Выводим категорию

    def show_booking_details_dialog(self):
        # Get the selected hotel and room
        selected_room = self.room_list.currentItem()
        if not selected_room:
            QMessageBox.warning(self, "Ошибка", "Выберите номер для бронирования!")
            return

        room_info = selected_room.text().split(" | ")[0]
        category = room_info.split(" ")[1].strip()  # Используем категорию вместо номера комнаты
        hotel_name = self.hotel_list.currentItem().text().split("(")[0].strip()

        # Show the dialog to enter user details and dates
        dialog = BookingDetailsDialog(self, hotel_name, category)  # Передаем категорию
        if dialog.exec():
            user_details = dialog.get_user_details()
            self.book_room_with_details(user_details)

    def book_room_with_details(self, user_details):
        try:
            check_in_date = user_details["check_in_date"]
            check_out_date = user_details["check_out_date"]

            # Проверка правильности дат
            if datetime.strptime(check_in_date, "%Y-%m-%d") >= datetime.strptime(check_out_date, "%Y-%m-%d"):
                QMessageBox.warning(self, "Ошибка", "Дата выезда должна быть позже даты заезда!")
                return

            # Получаем room_id из списка комнат
            room_id = self.rooms.get(user_details["category"])  # Используем категорию вместо номера комнаты
            if room_id is None:
                QMessageBox.warning(self, "Ошибка", "Номер не найден или недоступен!")
                return

            # Бронирование
            success = self.db_manager.book_room(self.user_id, room_id, check_in_date, check_out_date)
            if success:
                # После успешного бронирования, выводим сообщение
                QMessageBox.information(self, "Успешно",
                                        f"Вы забронировали номер категории {user_details['category']}.\n"
                                        "На ваш email были высланы реквизиты для оплаты. "
                                        "После оплаты администратор подтвердит вашу бронь.")

                # Обновление списка бронирований
                self.load_reservations()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось забронировать номер!")
        except Exception as e:
            # Логируем ошибку, чтобы понять, что не так
            print(f"Ошибка при бронировании: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при бронировании: {str(e)}")

    def load_reservations(self):
        self.booking_list.clear()
        bookings = self.db_manager.get_user_bookings(self.user_id)
        for b in bookings:
            b_id, hotel_name, category, check_in, check_out, status = b  # Вместо room_number используем category
            self.booking_list.addItem(
                f"ID: {b_id} | Отель: {hotel_name} | Категория: {category} | "  # Показываем категорию
                f"С: {check_in} | По: {check_out} | Статус: {status}"
            )


    def cancel_reservation(self):
        selected_booking = self.booking_list.currentItem()
        if not selected_booking:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование для отмены!")
            return

        booking_id = int(selected_booking.text().split(" | ")[0].split(": ")[1])
        success = self.db_manager.delete_booking(booking_id)
        if success:
            QMessageBox.information(self, "Успешно", "Бронирование успешно отменено.")
            self.load_reservations()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отменить бронирование.")
