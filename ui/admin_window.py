from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, QMessageBox,
                             QTabWidget, QInputDialog, QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QDialogButtonBox, QComboBox)
import datetime
import pytz
from openpyxl import Workbook
from PyQt6.QtWidgets import QFileDialog
class AddHotelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить отель")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.country_input = QLineEdit()  # Поле для ввода страны
        self.description_input = QLineEdit()
        self.rating_input = QSpinBox()
        self.rating_input.setRange(1, 5)
        self.rating_input.setValue(5)

        form_layout.addRow("Название отеля:", self.name_input)
        form_layout.addRow("Страна:", self.country_input)  # Добавлено поле
        form_layout.addRow("Описание:", self.description_input)
        form_layout.addRow("Рейтинг:", self.rating_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "country": self.country_input.text().strip(),  # Новое поле
            "description": self.description_input.text().strip(),
            "rating": self.rating_input.value(),
        }


class AddRoomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить номер")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.hotel_id_input = QSpinBox()
        self.hotel_id_input.setMinimum(1)

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 100)
        self.capacity_input.setValue(2)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setDecimals(2)
        self.price_input.setValue(1000.0)

        self.category_input = QComboBox()
        self.category_input.addItems(["Люкс", "Полулюкс", "Стандарт"])

        form_layout.addRow("ID отеля:", self.hotel_id_input)
        form_layout.addRow("Вместимость:", self.capacity_input)
        form_layout.addRow("Цена за ночь:", self.price_input)
        form_layout.addRow("Категория:", self.category_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        return {
            "hotel_id": self.hotel_id_input.value(),
            "capacity": self.capacity_input.value(),
            "price": self.price_input.value(),
            "category": self.category_input.currentText(),
        }
def get_moscow_time():
    moscow_tz = pytz.timezone("Europe/Moscow")
    return datetime.datetime.now(moscow_tz).strftime("%Y-%m-%d %H:%M:%S")

class AdminWindow(QWidget):
    def __init__(self, switch_window, db_manager):
        super().__init__(parent=None)
        self.switch_window = switch_window
        self.db_manager = db_manager
        self.setWindowTitle("Панель администратора")

        self.tabs = QTabWidget()
        self.setup_bookings_tab()
        self.setup_hotels_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.load_bookings()
        self.load_hotels()

        # Применяем стиль к кнопкам
        self.apply_button_styles()

    def apply_button_styles(self):
        button_style = """
        QPushButton {
            background-color: #007bff; /* Синий цвет */
            color: white; /* Белый текст */
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #0056b3; /* Темный синий при наведении */
            cursor: pointer;
        }

        QPushButton:pressed {
            background-color: #003f7f; /* Еще более темный синий при нажатии */
        }
        """

        # Применяем стиль ко всем кнопкам на форме
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)

    def setup_bookings_tab(self):
        self.bookings_tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Список всех бронирований"))
        self.booking_list = QListWidget()
        layout.addWidget(self.booking_list)

        button_layout = QHBoxLayout()

        confirm_button = QPushButton("Подтвердить")
        confirm_button.clicked.connect(lambda: self.change_booking_status("Подтверждено"))
        cancel_button = QPushButton("Отменить")
        cancel_button.clicked.connect(self.delete_booking)
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_bookings)
        export_button = QPushButton("Отчет")
        export_button.clicked.connect(self.export_bookings_to_excel)  # Добавляем обработчик кнопки
        logout_button = QPushButton("Выйти")
        logout_button.clicked.connect(lambda: self.switch_window("login"))

        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(export_button)  # Кнопка для экспорта
        button_layout.addWidget(logout_button)

        layout.addLayout(button_layout)
        self.bookings_tab.setLayout(layout)
        self.tabs.addTab(self.bookings_tab, "Бронирования")

    def export_bookings_to_excel(self):
        try:
            # Создаём новый Excel файл
            wb = Workbook()
            ws = wb.active
            ws.title = "Подтвержденные бронирования"

            # Добавляем заголовки
            headers = ["ID", "Пользователь", "Отель", "Номер", "С", "По", "Время бронирования", "Статус"]
            ws.append(headers)

            # Заполняем данные из базы, оставляя только подтверждённые
            bookings = self.db_manager.get_all_bookings()
            confirmed_bookings = [b for b in bookings if b[-1] == "Подтверждено"]

            for b in confirmed_bookings:
                ws.append(b)

            # Открываем диалог сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "Excel Files (*.xlsx);;All Files (*)"
            )

            if file_path:
                # Сохраняем файл
                wb.save(file_path)
                QMessageBox.information(self, "Успешно",
                                        f"Подтвержденные бронирования экспортированы в файл: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать бронирования: {str(e)}")

    def setup_hotels_tab(self):
        self.hotels_tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Список отелей"))
        self.hotels_list = QListWidget()
        layout.addWidget(self.hotels_list)

        button_layout = QHBoxLayout()

        add_hotel_button = QPushButton("Добавить отель")
        add_hotel_button.clicked.connect(self.add_hotel)

        add_room_button = QPushButton("Добавить номер")
        add_room_button.clicked.connect(self.add_room)

        refresh_hotels_button = QPushButton("Обновить")
        refresh_hotels_button.clicked.connect(self.load_hotels)

        button_layout.addWidget(add_hotel_button)
        button_layout.addWidget(add_room_button)
        button_layout.addWidget(refresh_hotels_button)

        layout.addLayout(button_layout)

        self.room_list_label = QLabel("Номера отеля")
        layout.addWidget(self.room_list_label)
        self.room_list = QListWidget()
        layout.addWidget(self.room_list)

        self.hotels_tab.setLayout(layout)
        self.tabs.addTab(self.hotels_tab, "Управление отелями")

        self.hotels_list.itemClicked.connect(self.load_rooms_for_selected_hotel)

    def load_bookings(self):
        self.booking_list.clear()
        bookings = self.db_manager.get_all_bookings()
        for b in bookings:
            b_id, user_name, hotel_name, room_num, check_in, check_out, booking_time, status = b
            booking_time_moscow = get_moscow_time()  # Вызываем независимую функцию
            self.booking_list.addItem(
                f"ID: {b_id} | Пользователь: {user_name} | Отель: {hotel_name} | Номер: {room_num} | "
                f"С: {check_in} | По: {check_out} | Время бронирования: {booking_time_moscow} | Статус: {status}"
            )

    def load_hotels(self):
        self.hotels_list.clear()
        hotels = self.db_manager.get_hotels()
        for h in hotels:
            h_id, name, country, desc, rating = h  # Убрано местоположение
            self.hotels_list.addItem(
                f"ID: {h_id} | {name} | {country} | Рейтинг: {rating} | {desc}"
            )

    def load_rooms_for_selected_hotel(self, item):
        self.room_list.clear()
        hotel_id = int(item.text().split(" | ")[0].split(": ")[1])
        rooms = self.db_manager.get_rooms_for_hotel(hotel_id)
        for room in rooms:
            room_id, category, capacity, price = room
            self.room_list.addItem(
                f"ID: {room_id} | Категория: {category} | Вместимость: {capacity} | Цена: {price} за ночь"
            )

    def add_hotel(self):
        dialog = AddHotelDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["name"] or not data["country"]:
                QMessageBox.warning(self, "Ошибка", "Название и страна обязательны.")
                return
            self.db_manager.add_hotel(
                name=data["name"],
                country=data["country"],  # Передаём страну
                description=data["description"],
                rating=data["rating"],
            )
            QMessageBox.information(self, "Успешно", f"Отель '{data['name']}' добавлен.")
            self.load_hotels()

    def add_room(self):
        current_item = self.hotels_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите отель для добавления номера!")
            return

        try:
            hotel_id = int(current_item.text().split(" | ")[0].split(": ")[1])
            dialog = AddRoomDialog(self)
            dialog.hotel_id_input.setValue(hotel_id)
            dialog.hotel_id_input.setDisabled(True)

            if dialog.exec():
                room_data = dialog.get_data()
                self.db_manager.add_room(
                    hotel_id=room_data["hotel_id"],
                    category=room_data["category"],
                    capacity=room_data["capacity"],
                    price=room_data["price"],
                )
                QMessageBox.information(self, "Успешно",
                                        f"Номер категории '{room_data['category']}' добавлен в отель ID={hotel_id}.")
                self.load_rooms_for_selected_hotel(current_item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def delete_booking(self):
        current_item = self.booking_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование для удаления!")
            return

        try:
            booking_id = int(current_item.text().split(" | ")[0].split(": ")[1])
            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить бронирование ID={booking_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.db_manager.delete_booking(booking_id)
                QMessageBox.information(self, "Успешно", f"Бронирование ID={booking_id} удалено.")
                self.load_bookings()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить бронирование: {str(e)}")

    def change_booking_status(self, status):
        current_item = self.booking_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите бронирование для изменения статуса!")
            return

        try:
            booking_id = int(current_item.text().split(" | ")[0].split(": ")[1])
            self.db_manager.update_booking_status(booking_id, status)
            QMessageBox.information(self, "Успешно", f"Статус бронирования ID={booking_id} изменён на '{status}'.")
            self.load_bookings()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус бронирования: {str(e)}")


