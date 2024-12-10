from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, switch_window, db_manager):
        super().__init__()
        self.switch_window = switch_window
        self.db_manager = db_manager
        self.setWindowTitle("Hotel Booking System")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        """)

        # Поле ввода email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите ваш email")
        self.email_input.setStyleSheet("""
            QLineEdit {
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
                border: 2px solid #007BFF;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0056b3;
            }
        """)

        # Кнопка входа
        login_button = QPushButton("Войти")
        login_button.setStyleSheet("""
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
        login_button.clicked.connect(self.login)

        # Кнопка регистрации
        register_button = QPushButton("Зарегистрироваться")
        register_button.setStyleSheet("""
            QPushButton {
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
        register_button.clicked.connect(lambda: self.switch_window("register"))

        # Расположение элементов
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(login_button)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        user = self.db_manager.check_user_credentials(email, password)
        if user:
            user_id, user_name, role = user
            QMessageBox.information(self, "Успешно", f"Добро пожаловать, {user_name}!")
            self.switch_window("admin" if role == "admin" else "customer", user_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль!")
