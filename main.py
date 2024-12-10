import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from database import DatabaseManager
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.admin_window import AdminWindow
from ui.customer_window import CustomerWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager("hotel_booking.db")
        self.db_manager.initialize_database()

        self.setWindowTitle("Hotel Booking System")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_window = LoginWindow(self.switch_window, self.db_manager)
        self.register_window = RegisterWindow(self.switch_window, self.db_manager)
        self.admin_window = AdminWindow(self.switch_window, self.db_manager)
        self.customer_window = None

        self.stack.addWidget(self.login_window)
        self.stack.addWidget(self.register_window)
        self.stack.addWidget(self.admin_window)

        self.switch_window("login")

    def switch_window(self, window_name, user_id=None):
        if window_name == "login":
            self.stack.setCurrentWidget(self.login_window)
            self.setFixedSize(400, 300)
        elif window_name == "register":
            self.stack.setCurrentWidget(self.register_window)
            self.setFixedSize(400, 300)
        elif window_name == "admin":
            self.stack.setCurrentWidget(self.admin_window)
            self.setFixedSize(800, 600)
        elif window_name == "customer":
            if self.customer_window is None:
                self.customer_window = CustomerWindow(self.switch_window, self.db_manager, user_id)
                self.stack.addWidget(self.customer_window)
            self.stack.setCurrentWidget(self.customer_window)
            self.setFixedSize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
