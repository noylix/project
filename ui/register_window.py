from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class RegisterWindow(QWidget):
    def __init__(self, switch_window, db_manager):
        super().__init__()
        self.switch_window = switch_window
        self.db_manager = db_manager
        self.setWindowTitle("Регистрация")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """)

        # Поле ввода имени
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ваше имя")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)

        # Поле ввода email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите ваш email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)

        # Поле ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)

        # Кнопка регистрации
        register_button = QPushButton("Зарегистрироваться")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d80;
            }
        """)
        register_button.clicked.connect(self.register_user)

        # Кнопка возврата
        back_button = QPushButton("Назад")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #007BFF;
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
            }
            QPushButton:pressed {
                background-color: #e0e7ff;
            }
        """)
        back_button.clicked.connect(lambda: self.switch_window("login"))

        # Расположение элементов
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(register_button)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def register_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not email or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        success = self.db_manager.register_user(name, email, password)
        if success:
            QMessageBox.information(self, "Успешно", "Регистрация прошла успешно!")
            self.switch_window("login")
        else:
            QMessageBox.warning(self, "Ошибка", "Email уже существует!")
