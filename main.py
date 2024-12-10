import sys
from ssl import socket_error

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                           QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPainter, QPixmap
import os

from audio import Windows
from camera_view import CameraViewWindow
from face import EmotionApp



class FeatureCard(QPushButton):
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setFixedSize(380, 200)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                border-radius: 15px;
                padding: 15px;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet('color: white; background: transparent;')
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet('color: #BBBBBB; background: transparent;')
        desc_label.setFont(QFont('Arial', 12))
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        # Prevent labels from interfering with button clicks
        super().mousePressEvent(event)

class SidebarButton(QPushButton):
    def __init__(self, icon_path, text):
        super().__init__()
        self.setText(text)
        
        # Создаем белую версию иконки
        icon = QIcon(icon_path)
        pixmap = icon.pixmap(QSize(20, 20))
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), Qt.white)
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(20, 20))
        
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                border: none;
                color: #CCCCCC;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #424242;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """)
        self.clicked.connect(self.button_clicked)
        
    def button_clicked(self):
        # Получаем текст кнопки и выполняем соответствующее действие
        action = self.text()
        if action == "Просмотр":
            print("Открываю просмотр...")
        elif action == "Конфигурация тревог":
            print("Открываю конфигурацию тревог...")
        elif action == "Конфигурация системы":
            print("Открываю конфигурацию системы...")
        elif action == "Ресурс последовательности":
            print("Открываю ресурс последовательности...")
        elif action == "Управление пользователями":
            print("Открываю управление пользователями...")
        elif action == "Расписания записи":
            print("Открываю расписания записи...")
        elif action == "Журнал операций":
            print("Открываю журнал операций...")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Система видеонаблюдения')
        self.setStyleSheet('background-color: #333333;')
        self.setFixedSize(1550, 800)
        
        # Create top navigation
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border-bottom: 2px solid #505050;
                margin: 0;
                padding: 0;
            }
        """)
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        nav_buttons = [
            ('Просмотр', self.on_view_click),
            ('Просмотр камер', self.on_cameras_click),
            ('Записи', self.on_records_click),
            ('Настройки видео', self.on_video_settings_click),
            ('Настройки аудио', self.on_audio_settings_click)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #424242;
                    color: white;
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-size: 14px;
                    text-align: left;
                    border-bottom: 2px solid #505050;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border-bottom: 2px solid #606060;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
            """)
            nav_layout.addWidget(btn)
        
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_widget.setLayout(nav_layout)
        
        # Create main content area
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        
        # Left section with grid
        left_section = QWidget()
        left_layout = QVBoxLayout()
        
        # Grid for feature cards
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        features = [
            ('Живой просмотр', 'Просмотр видео в реальном времени и управление экраном'),
            ('Воспроизведение', 'Поиск и воспроизведение записей'),
            ('Видеостена', 'Использование и редактирование видеостены'),
            ('Аудио', 'Двусторонняя аудиосвязь и трансляция'),
            ('Электронная карта', 'Добавление, редактирование и удаление электронных карт'),
            ('Подсчет людей', 'Количество людей, которых можно выделять и просматривать'),
            ('Записи по тревоге', 'Просмотр сигналов и тревог в реальном времени'),
            ('Диспетчер устройств', 'Добавление, редактирование, удаление и настройка устройств'),
            ('Распознавание людей', 'Распознавать людей в реальном времени')
        ]
        
        for i, (title, desc) in enumerate(features):
            card = FeatureCard(title, desc)
            card.clicked.connect(lambda checked, t=title: self.on_feature_click(t))
            grid_layout.addWidget(card, i // 3, i % 3)
        
        grid_widget.setLayout(grid_layout)
        left_layout.addWidget(grid_widget)
        left_section.setLayout(left_layout)
        
        # Right section with sidebar
        right_section = QWidget()
        right_section.setStyleSheet("""
            QWidget {
                border-left: 2px solid #505050;
                background-color: #333333;
                margin: 0;
                padding: 0;
                height: 100%;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add section title
        sidebar_title = QLabel("Настройки и управление")
        sidebar_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #424242;
                border-radius: 5px;
                border-bottom: 2px solid #505050;
                margin: 5px;
            }
        """)
        right_layout.addWidget(sidebar_title)
        
        # Sidebar buttons
        sidebar_buttons = [
            ('Просмотр', 'television.svg'),
            ('Конфигурация тревог', 'alert-octagon-outline.svg'),
            ('Конфигурация системы', 'cog.svg'),
            ('Ресурс последовательности', 'file-account-outline.svg'),
            ('Управление пользователями', 'account-multiple-outline.svg'),
            ('Расписания записи', 'video-plus-outline.svg'),
            ('Журнал операций', 'laptop.svg')
        ]
        
        for text, icon_file in sidebar_buttons:
            icon_path = os.path.join(os.path.dirname(__file__), 'icons', icon_file)
            btn = SidebarButton(icon_path, text)
            right_layout.addWidget(btn)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), 'icons', 'rzhd_white.png')
        logo_pixmap = QPixmap(logo_path)
        # Увеличиваем размер логотипа до 250x250 пикселей
        logo_pixmap = logo_pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        
        # Добавляем немного пустого места перед логотипом (40% от оставшегося пространства)
        spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_layout.addItem(spacer)
        right_layout.addWidget(logo_label)
        # Оставляем меньше места после логотипа (60% от оставшегося пространства)
        spacer_bottom = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_layout.addItem(spacer_bottom)
        
        right_layout.setStretch(right_layout.count()-3, 40)  # Пространство перед логотипом
        right_layout.setStretch(right_layout.count()-1, 60)  # Пространство после логотипа
        
        right_section.setLayout(right_layout)
        right_section.setFixedWidth(300)  # Увеличил ширину для лучшей читаемости
        
        # Add sections to content layout
        content_layout.addWidget(left_section)
        content_layout.addWidget(right_section)
        content_widget.setLayout(content_layout)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
        main_layout.setSpacing(0)  # Убираем пространство между элементами
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget)
        
        # Устанавливаем растягивание для content_widget
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_widget.setLayout(main_layout)
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
    def on_view_click(self):
        self.class_emotion = EmotionApp()
        self.class_emotion.show()
        
    def on_cameras_click(self):
        self.camera_window = CameraViewWindow()
        self.camera_window.show()
        
    def on_records_click(self):
        self.audio_window = Windows()
        self.audio_window.show()
        
    def on_video_settings_click(self):
        print("Настройки видео clicked")
        
    def on_audio_settings_click(self):
        print("Настройки аудио clicked")
        
    def on_feature_click(self, title):
        print(f"{title} clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
