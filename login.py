import os
import time

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import subprocess  # Import subprocess

# Определение цветов
colors = {
    "RZD_Red": "#e21a1a",
    "White": "#ffffff",
    "Gray_BG": "#f0f0f0",
    "Light_Gray": "#e0e0e0",
    "Dark_Text": "#333333"
}

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в аккаунт")
        self.setStyleSheet(f"background-color: {colors['White']};")

        # Основной горизонтальный макет
        main_layout = QHBoxLayout()

        # Левая панель с формой входа
        self.init_left_panel(main_layout)

        # Правая панель с изображением
        self.init_right_panel(main_layout)

        # Установка основного макета
        self.setLayout(main_layout)

    def init_left_panel(self, main_layout):
        # Левая панель
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Заголовок формы
        title = QLabel("Вход в аккаунт")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {colors['Dark_Text']}; padding: 10px;")

        # Формат полей формы
        form_layout = QFormLayout()

        # Поля ввода
        email_label, email_input = self.create_input("Эл. почта", "Введите вашу почту")
        password_label, password_input = self.create_input("Пароль", "Введите ваш пароль", is_password=True)

        form_layout.addRow(email_label, email_input)
        form_layout.addRow(password_label, password_input)

        # Кнопка входа
        login_button = QPushButton("Войти")
        login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['RZD_Red']}; 
                color: {colors['White']};
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #ff4d4d;
            }}
        """)

        # Connect the login button to the login method
        login_button.clicked.connect(self.login)  # Connect button click to login method

        # Текст ссылки на регистрацию
        register_label = QLabel("Нет аккаунта? <a href='#'>Зарегистрируйтесь</a>")
        register_label.setStyleSheet(f"color: {colors['RZD_Red']}; font-size: 12px;")
        register_label.setTextFormat(Qt.RichText)
        register_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        register_label.setOpenExternalLinks(True)

        # Добавление элементов в левую панель
        left_layout.addWidget(title, alignment=Qt.AlignLeft)
        left_layout.addLayout(form_layout)
        left_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(register_label, alignment=Qt.AlignCenter)

        # Настройка левой панели
        left_panel.setLayout(left_layout)
        left_panel.setStyleSheet(f"background-color: {colors['Gray_BG']}; border-radius: 20px; padding: 20px;")

        main_layout.addWidget(left_panel, 2)

    def init_right_panel(self, main_layout):
        # Правая панель с изображением
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Загрузка изображения (замените путь на изображение на ваш путь)
        train_image = QLabel()
        pixmap = QPixmap("icons/login.png")
        train_image.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        train_image.setAlignment(Qt.AlignCenter)

        # Оформление правой панели
        right_panel.setStyleSheet(f"background-color: {colors['RZD_Red']}; border-radius: 20px;")
        right_layout.addWidget(train_image, alignment=Qt.AlignCenter)
        right_panel.setLayout(right_layout)

        main_layout.addWidget(right_panel, 1)

    def create_input(self, label_text, placeholder_text, is_password=False):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        # Стилизация полей ввода
        input_field.setStyleSheet(f"""
            padding: 10px; 
            background-color: {colors['Light_Gray']}; 
            border: 1px solid {colors['Light_Gray']};
            border-radius: 8px;
            color: {colors['Dark_Text']};
        """)

        label.setStyleSheet(f"color: {colors['Dark_Text']}; font-weight: bold;")
        return label, input_field

    def login(self):
        """Open the main window script and close the login window."""
        os.system('python main.py')
        time.sleep(7)# Adjust the command if necessary
        self.close()  # Close the login window

app = QApplication([])
window = LoginWindow()
window.resize(800, 500)
window.show()
app.exec_()
