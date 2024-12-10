import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
import random  # Для тестового обновления значений
import torch
import torch.nn.functional as F
from transformers import AutoConfig, Wav2Vec2Processor, AutoModelForAudioClassification
import sounddevice as sd
import threading
import numpy as np

# Устройство (GPU если доступно)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Модель и конфиг для эмоций
model_name_or_path = "soundmodel"
config = AutoConfig.from_pretrained(model_name_or_path)
processor = Wav2Vec2Processor.from_pretrained(model_name_or_path)
sampling_rate = processor.feature_extractor.sampling_rate
model = AutoModelForAudioClassification.from_pretrained(model_name_or_path, trust_remote_code=True).to(device)

# Функция для записи аудио
def record_audio(duration=2, sampling_rate=16000):
    print(f"Запись звука в течение {duration} секунд...")
    audio = sd.rec(int(duration * sampling_rate), samplerate=sampling_rate, channels=1, dtype='float32')
    sd.wait()
    print("Запись завершена.")
    return audio.flatten()

# Функция предсказания эмоции с использованием модели
def predict_emotion(audio):
    # Преобразуем аудио в нужный формат
    features = processor(audio, sampling_rate=sampling_rate, return_tensors="pt", padding=True)

    # Переносим на устройство
    input_values = features.input_values.to(device)
    attention_mask = features.attention_mask.to(device)

    with torch.no_grad():
        # Получаем логиты от модели
        logits = model(input_values, attention_mask=attention_mask).logits

    # Применяем softmax для получения вероятностей
    scores = F.softmax(logits*0.3, dim=1).detach().cpu().numpy()[0]

    # Создаем список с метками и вероятностями, сортируем по убыванию вероятности
    emotion_probabilities = [{"label": config.id2label[i], "score": round(score, 5)} for i, score in enumerate(scores)]

    return emotion_probabilities
emotions = np.array([0 for i in range(5)],dtype=np.float32)
outemotions=np.zeros((5,),dtype=np.float32)
# Главный цикл для реального времени
def real_time_emotion_recognition():
    print("Начало анализа эмоций. Нажмите Ctrl+C для выхода.")
    try:
        while True:
            audio = record_audio(duration=3)  # Запись 5 секунд аудио
            emotion_probabilities = predict_emotion(audio)
            print("Эмоции с вероятностями (от большей к меньшей):")
            emotions[4]=emotion_probabilities[4]['score']
            emotions[0] = emotion_probabilities[2]['score']
            emotions[1] = emotion_probabilities[0]['score']
            emotions[3] = emotion_probabilities[1]['score']
            emotions[2] = emotion_probabilities[3]['score']
            for emotion in emotion_probabilities:
                print(f"{emotion['label']}: {emotion['score']}")
    except KeyboardInterrupt:
        print("Анализ завершен.")
threading.Thread(target=real_time_emotion_recognition, daemon=True).start()
#sad neutral angry happy other
class Windows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Основное приложение')
        self.setStyleSheet('background-color: #333333;')
        self.setMinimumSize(1200, 800)
        self.progress_bars = []  # Список для хранения прогресс-баров
        
        # Инициализация таймера для обновления каждый кадр
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(16)  # 60 FPS (1000ms / 60 ≈ 16ms)
        
        self.setup_ui()

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
            'Просмотр данных',
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

        # Основная область контента (пустая для будущего использования)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Добавляем основной контент
        main_layout.addWidget(content_widget)

        # Гистограмма из 5 элементов, расположенная по горизонтали, но с ростом вверх
        histogram_widget = QWidget()
        histogram_layout = QHBoxLayout(histogram_widget)
        histogram_layout.setContentsMargins(50, 20, 50, 10)
        histogram_layout.setSpacing(50)  # Увеличиваем пространство между прогресс-барами

        # Тексты для каждого прогресс-бара
        labels = ["Грустный", "Нейтральный", "Злой", "Весёлый", "Прочее"]

        # Создаем 5 вертикальных контейнеров для каждого прогресс-бара с подписью снизу
        for i in range(5):
            # В вертикальном контейнере будут прогресс-бар и текст
            container = QVBoxLayout()

            # Создаем вертикальный прогресс-бар
            progress = QProgressBar()
            progress.setValue((i + 1) * 20)  # Пример значений от 20 до 100
            progress.setOrientation(Qt.Vertical)  # Устанавливаем вертикальную ориентацию
            progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #505050;
                    border-radius: 5px;
                    background-color: #424242;
                    text-align: center;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: red;
                    border-radius: 5px;
                }
            """)
            progress.setFixedWidth(120)  # Ширина прогресс-бара (увеличена в 3 раза)
            progress.setMaximumHeight(600)  # Высота прогресс-бара (увеличена в 3 раза)
            self.progress_bars.append(progress)  # Добавляем прогресс-бар в список

            # Создаем контейнер для метки, чтобы контролировать её ширину
            label_container = QWidget()
            label_container.setFixedWidth(120)  # Такая же ширина, как у progress bar
            label_layout = QHBoxLayout(label_container)
            label_layout.setContentsMargins(0, 5, 0, 0)  # Уменьшаем отступы

            # Добавляем текст под прогресс-баром
            label = QLabel(labels[i])
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: transparent;
                    font-size: 12px;
                }
            """)
            label_layout.addWidget(label)

            # Добавляем виджеты в вертикальный контейнер
            container.addWidget(progress)
            container.addWidget(label_container)
            container.setAlignment(Qt.AlignHCenter)  # Центрируем всё содержимое

            # Добавляем контейнер в основной макет
            histogram_layout.addLayout(container)

        # Добавляем гистограмму в основной макет
        main_layout.addWidget(histogram_widget)

    def update_progress_bars(self, values):
        """
        Обновляет значения прогресс-баров.
        :param values: список из 5 значений от 0 до 100 для каждого прогресс-бара
        """
        if len(values) != 5:
            print("Ошибка: необходимо передать 5 значений")
            return
        
        for i, value in enumerate(values):
            # Убеждаемся, что значение находится в диапазоне от 0 до 100
            value = max(0, min(100, value))
            self.progress_bars[i].setValue(value)

    def update_frame(self):
        global outemotions
        """
        Функция вызывается каждый кадр (60 раз в секунду)
        Здесь можно получать данные и обновлять прогресс-бары
        """
        outemotions=outemotions*0.98+emotions*0.02
        # Пример: генерация случайных значений для тестирования
        # В реальном приложении здесь будет логика получения актуальных данных
        self.update_progress_bars(outemotions*100)
