import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from deepface import DeepFace
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QProgressBar, QWidget, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from threading import Thread

# Цветовая палитра
colors = {
    "RZD_Red": "#e21a1a",
    "White": "#ffffff",
    "Gray_BG": "#f0f0f0",
    "Light_Gray": "#e0e0e0",
    "Dark_Text": "#333333"
}

class EmotionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация захвата видео и GUI элементов
        self.video_capture = cv2.VideoCapture(1)
        self.target_emotions = {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}
        
        # Таймер для обновления видеокадра
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        # Левая секция для видеопотока
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet(f"background-color: {colors['Gray_BG']}; border: 2px solid {colors['Light_Gray']};")

        # Правая секция для эмоций
        self.emotion_labels = []
        self.emotion_bars = []
        layout_emotions = QVBoxLayout()
        
        # Создаем текстовые метки и прогресс-бары для эмоций
        for emotion in self.target_emotions.keys():
            label = QLabel(emotion + ": 0%")
            label.setStyleSheet(f"color: {colors['Dark_Text']}; font-size: 14px; font-weight: bold;")
            
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors['Light_Gray']};
                    text-align: center;
                    color: {colors['White']};
                    background-color: {colors['Gray_BG']};
                }}
                QProgressBar::chunk {{
                    background-color: {colors['RZD_Red']};
                }}
            """)
            self.emotion_labels.append(label)
            self.emotion_bars.append(bar)
            layout_emotions.addWidget(label)
            layout_emotions.addWidget(bar)

        # Основной макет
        layout_main = QHBoxLayout()
        layout_main.addWidget(self.video_label)
        layout_main.addLayout(layout_emotions)
        self.setLayout(layout_main)

        # Основные настройки окна
        self.setWindowTitle("Emotion Detector")
        self.setGeometry(100, 100, 900, 500)
        self.setStyleSheet(f"background-color: {colors['White']};")
        
        # Переменные для потока анализа
        self.analysis_thread = None
        self.current_frame = None

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.current_frame = frame.copy()  # Сохраняем текущий кадр
            
            # Запускаем анализ эмоций в отдельном потоке, если поток не активен
            if self.analysis_thread is None or not self.analysis_thread.is_alive():
                self.analysis_thread = Thread(target=self.analyze_emotions, args=(frame,))
                self.analysis_thread.start()

            # Отображаем видеокадр в QLabel без использования QPainter
            self.analysis_thread.join()
            
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            step = channel * width
            q_image = QImage(rgb_image.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def analyze_emotions(self, frame):
        # Уменьшаем размер кадра для ускорения анализа
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        try:
            # Анализируем эмоции на уменьшенном кадре
            analysis = DeepFace.analyze(small_frame, actions=['emotion'])
            self.target_emotions = analysis[0]['emotion']
        except Exception as e:
            print('Face not found', e)

        # Обновляем текстовые метки и прогресс-бары с интерполяцией
        try:
            for i, (emotion, target_value) in enumerate(self.target_emotions.items()):
                current_value = self.emotion_bars[i].value()
                smoothed_value = int(current_value + 0.1 * (target_value - current_value))
                self.emotion_labels[i].setText(f"{emotion}: {smoothed_value}%")
                self.emotion_bars[i].setValue(smoothed_value)
            
        except:
            pass
    def closeEvent(self, event):
        # Очищаем ресурсы при закрытии окна
        self.video_capture.release()
        cv2.destroyAllWindows()
        event.accept()


