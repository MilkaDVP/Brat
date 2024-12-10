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

class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация аккаунта")
        self.setStyleSheet(f"background-color: {colors['White']};")

        # Основной горизонтальный макет
        main_layout = QHBoxLayout()

        # Левая панель с изображением
        self.init_left_panel(main_layout)

        # Правая панель с формой регистрации
        self.init_right_panel(main_layout)

        # Установка основного макета
        self.setLayout(main_layout)

    def init_left_panel(self, main_layout):
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Загрузка изображения (замените путь на изображение на ваш путь)
        train_image = QLabel()
        pixmap = QPixmap("icons/registration.png")
        train_image.setPixmap(pixmap.scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        train_image.setAlignment(Qt.AlignCenter)

        # Оформление левой панели
        left_panel.setStyleSheet(f"background-color: {colors['RZD_Red']}; border-radius: 20px;")
        left_layout.addWidget(train_image, alignment=Qt.AlignCenter)
        left_panel.setLayout(left_layout)

        main_layout.addWidget(left_panel, 1)

    def init_right_panel(self, main_layout):
        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Заголовок формы
        title = QLabel("Регистрация аккаунта")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {colors['Dark_Text']}; padding: 10px;")

        # Формат полей формы
        form_layout = QFormLayout()

        # Поля ввода
        full_name_label, full_name_input = self.create_input("Полное ФИО", "Введите ФИО сотрудника")
        email_label, email_input = self.create_input("Почта сотрудника", "Введите почту сотрудника")
        password_label, password_input = self.create_input("Пароль", "Введите пароль сотрудника", is_password=True)

        form_layout.addRow(full_name_label, full_name_input)
        form_layout.addRow(email_label, email_input)
        form_layout.addRow(password_label, password_input)

        # Кнопка регистрации
        register_button = QPushButton("Создать аккаунт")
        register_button.setStyleSheet(f"""
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

        # Текст ссылки на вход
        login_label = QLabel("Уже есть аккаунт? <a href='#'>Войдите</a>")
        login_label.setStyleSheet(f"color: {colors['RZD_Red']}; font-size: 12px;")
        login_label.setTextFormat(Qt.RichText)
        login_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        login_label.setOpenExternalLinks(False)  # Disable external link opening

        # Connect the link click to the login method
        login_label.linkActivated.connect(self.open_login)  # Connect link to open_login method

        # Добавление элементов в правую панель
        right_layout.addWidget(title, alignment=Qt.AlignLeft)
        right_layout.addLayout(form_layout)
        right_layout.addWidget(register_button, alignment=Qt.AlignCenter)
        right_layout.addWidget(login_label, alignment=Qt.AlignCenter)

        # Настройка правой панели
        right_panel.setLayout(right_layout)
        right_panel.setStyleSheet(f"background-color: {colors['Gray_BG']}; border-radius: 20px; padding: 20px;")

        main_layout.addWidget(right_panel, 2)

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

    def open_login(self):
        """Open the login script and close the registration window."""
        subprocess.Popen(["python", "login.py"])
        # Adjust the command if necessary
        self.close()  # Close the registration window

app = QApplication([])
window = RegistrationWindow()
window.resize(800, 500)
window.show()
app.exec_()
