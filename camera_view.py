import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QScrollArea, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QMouseEvent, QResizeEvent, QImage
import cv2
import numpy as np

import socket
import threading
import subprocess


def client_handler(connection):
    while True:
        data = connection.recv(1024)
        if data:
            print('Полученные данные:', data.decode('utf-8'), end='\n')
            connection.send(data)
        else:
            break
    connection.close()

active_sockets={}


class DraggableCameraWidget(QWidget):
    def __init__(self, camera_id, main_window, parent=None):
        super().__init__(parent)
        self.mainwindow=main_window
        self.camera_id = camera_id
        self.setMinimumSize(320, 240)
        self.setMaximumSize(1920, 1080)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QWidget {
                background-color: #424242;
                border: none;
            }
        """)
        
        # Для перетаскивания
        self.dragging = False
        self.offset = QPoint()
        
        # Для изменения размера
        self.resizing = False
        self.resize_start = QPoint()
        self.original_size = QSize()
        
        # Для масштабирования
        self.is_fullscreen = False
        self.original_geometry = None
        
        self.setMouseTracking(True)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок только с кнопкой закрытия
        header = QWidget()
        header.setFixedHeight(25)
        header.setStyleSheet("background-color: #505050; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 2, 5, 2)
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(close_btn)
        
        # Метка для видео
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: none; background-color: #424242;")
        self.video_label.setMinimumSize(320, 240)
        
        layout.addWidget(header)
        layout.addWidget(self.video_label)
        
        # Инициализация камеры
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_fullscreen:
                # Сохраняем текущую геометрию
                self.original_geometry = self.geometry()
                # Расширяем до размеров родительского виджета
                parent_rect = self.parent().rect()
                self.setGeometry(parent_rect)
                self.is_fullscreen = True
            else:
                # Возвращаем исходный размер
                if self.original_geometry:
                    self.setGeometry(self.original_geometry)
                self.is_fullscreen = False

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                widget_size = self.video_label.size()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                print(frame_rgb.shape,frame_rgb.dtype,len(frame_rgb.tobytes()))
                active_sockets[self.camera_id].send(frame_rgb.tobytes())
                frame_rgb=np.frombuffer(active_sockets[self.camera_id].recv(230400 * 4),dtype=np.uint8).reshape((480,640,3))

                frame_rgb = cv2.resize(frame_rgb, (widget_size.width(), widget_size.height()))
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_BGR888)
                
                # Масштабируем изображение точно под размер виджета
                
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    widget_size.width(), 
                    widget_size.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Создаем пустой pixmap размером с виджет
                final_pixmap = QPixmap(widget_size)
                final_pixmap.fill(Qt.transparent)
                
                # Рисуем scaled_pixmap по центру
                painter = QPainter(final_pixmap)
                x = (widget_size.width() - scaled_pixmap.width()) // 2
                y = (widget_size.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                self.video_label.setPixmap(final_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Определяем область для изменения размера (правый нижний угол)
            resize_rect = QRect(self.width() - 20, self.height() - 20, 20, 20)
            if resize_rect.contains(event.pos()):
                self.resizing = True
                self.resize_start = event.globalPos()
                self.original_size = self.size()
            else:
                self.dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
        elif self.resizing:
            diff = event.globalPos() - self.resize_start
            new_width = max(320, min(1920, self.original_size.width() + diff.x()))
            new_height = max(240, min(1080, self.original_size.height() + diff.y()))
            self.resize(new_width, new_height)
        else:
            # Изменение курсора при наведении на угол для изменения размера
            resize_rect = QRect(self.width() - 20, self.height() - 20, 20, 20)
            if resize_rect.contains(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        active_sockets[self.camera_id].close()
        super().closeEvent(event)

class CameraViewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Просмотр камер')
        self.setStyleSheet('background-color: #333333;')
        self.setMinimumSize(1200, 800)
        
        # Поиск доступных камер
        self.available_cameras = self.find_cameras()
        
        # Список активных камер
        self.active_cameras = []
        self.active_sockets={}
        self.server = socket.socket(-1, -1)
        self.server.bind(('localhost', 8080))
        self.server.listen()
        print('server started')
        self.setup_ui()

    def find_cameras(self):
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        return available_cameras
        
    def setup_ui(self):
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель с кнопками
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: #333333;
                border-bottom: 2px solid #505050;
            }
        """)
        nav_layout = QHBoxLayout()
        nav_buttons = [
            'Панель управления',
            'Просмотр камер',
            'Записи',
            'Настройки видео',
            'Настройки аудио'
        ]
        
        for text in nav_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
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
                }
            """)
            nav_layout.addWidget(btn)
        
        nav_widget.setLayout(nav_layout)
        main_layout.addWidget(nav_widget)
        
        # Основной контент
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Левая панель с кнопками камер
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #424242;
                border-right: 2px solid #505050;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок левой панели
        title_label = QLabel("Доступные камеры")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #505050;
                border-radius: 5px;
            }
        """)
        left_layout.addWidget(title_label)
        
        # Кнопки камер
        camera_button_style = """
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
                margin: 2px 5px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """
        
        if self.available_cameras:
            for cam_id in self.available_cameras:
                btn = QPushButton(f"Камера {cam_id}")
                btn.setStyleSheet(camera_button_style)
                btn.clicked.connect(lambda checked, cam_id=cam_id: self.add_camera(cam_id))
                left_layout.addWidget(btn)
        else:
            no_cameras_label = QLabel("Камеры не найдены")
            no_cameras_label.setStyleSheet("color: white;")
            left_layout.addWidget(no_cameras_label)
        
        left_layout.addStretch()
        
        # Правая панель для отображения камер
        self.camera_area = QWidget()
        self.camera_area.setStyleSheet("background-color: #333333;")
        
        # Добавляем панели в основной layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(self.camera_area, stretch=1)
        
        main_layout.addWidget(content_widget)
        
    def add_camera(self, camera_id):
        os.system(os.path.abspath(os.path.dirname(__file__))+'\start.bat')
        connection, address = self.server.accept()
        active_sockets[camera_id] = connection
        camera_widget = DraggableCameraWidget(camera_id, self.camera_area,self)
        camera_widget.move(50 + len(self.active_cameras) * 30, 50 + len(self.active_cameras) * 30)
        camera_widget.show()
        self.active_cameras.append(camera_widget)

    def closeEvent(self, event):
        # Закрываем все активные камеры
        for camera in self.active_cameras:
            camera.close()
        super().closeEvent(event)
