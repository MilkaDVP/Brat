# Система видеонаблюдения с распознаванием эмоций

Система видеонаблюдения с возможностью распознавания эмоций на основе нейронных сетей, использующая датасеты Dusha и Emotic для анализа эмоционального состояния людей в реальном времени.

## Описание проекта

Проект представляет собой комплексную систему видеонаблюдения с следующими возможностями:
- Распознавание лиц и эмоций в реальном времени
- Анализ аудио для определения эмоционального состояния
- Многокамерный мониторинг
- Запись и воспроизведение видео
- Управление правами пользователей
- Настройка тревожных событий

## Используемые датасеты

### Emotic Dataset
Emotic (EMOTIon recognition in Context) - это датасет, который содержит изображения людей в различных реальных ситуациях с аннотациями их эмоциональных состояний. Датасет включает:
- 26 категорий дискретных эмоций
- 3 непрерывных измерения эмоционального состояния (Valence, Arousal, Dominance)
- Более 34,000 аннотированных изображений

### Dusha Dataset
Dusha - это специализированный датасет для распознавания эмоций, который включает:
- Аудио записи эмоциональной речи
- Визуальные данные выражений лица
- Мультимодальные признаки для более точного распознавания эмоций

## 26 категорий эмоций

Система распознает следующие 26 категорий эмоций:

1. Affection (Привязанность)
2. Anger (Гнев)
3. Annoyance (Раздражение)
4. Anticipation (Предвкушение)
5. Aversion (Отвращение)
6. Confidence (Уверенность)
7. Disapproval (Неодобрение)
8. Disconnection (Отстраненность)
9. Disquietment (Беспокойство)
10. Doubt/Confusion (Сомнение/Замешательство)
11. Engagement (Вовлеченность)
12. Esteem (Уважение)
13. Excitement (Возбуждение)
14. Fatigue (Усталость)
15. Fear (Страх)
16. Happiness (Счастье)
17. Pain (Боль)
18. Peace (Умиротворение)
19. Pleasure (Удовольствие)
20. Sadness (Грусть)
21. Sensitivity (Чувствительность)
22. Suffering (Страдание)
23. Surprise (Удивление)
24. Sympathy (Сочувствие)
25. Yearning (Тоска)
26. None (Отсутствие выраженной эмоции)

## Технические характеристики

- Язык программирования: Python
- Графический интерфейс: PyQt5
- Нейронные сети: PyTorch
- Обработка изображений: OpenCV
- Обработка аудио: librosa

## Основные компоненты

- `main.py` - главное окно приложения
- `emotion_detection.py` - модуль распознавания эмоций
- `audio.py` - модуль обработки аудио
- `camera_view.py` - модуль работы с камерами
- `face.py` - модуль распознавания лиц
- `login.py` и `registration.py` - модули аутентификации

## Установка и запуск

1. Клонируйте репозиторий
2. Установите необходимые зависимости:
```bash
pip install torch torchvision opencv-python PyQt5 numpy pillow librosa
```
3. Запустите приложение:
```bash
python main.py
```

## Особенности реализации

- Использование архитектуры ResNet для извлечения признаков из изображений
- Комбинированный анализ контекста и выражения лица для повышения точности
- Batch Normalization и Dropout для предотвращения переобучения
- Многопоточная обработка для оптимальной производительности

## Примечания

- Для работы с GPU требуется CUDA-совместимая видеокарта
- Модели предварительно обучены на датасетах Emotic и Dusha
- Система поддерживает многокамерный режим работы

## Citations

[1] Kosti, Ronak, Jose M. Alvarez, Adria Recasens, and Agata Lapedriza. "Context based emotion recognition using emotic dataset." IEEE transactions on pattern analysis and machine intelligence 42, no. 11 (2019): 2755-2766.
[2] Kosti, Ronak, Jose M. Alvarez, Adria Recasens, and Agata Lapedriza. "Emotion recognition in context." In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 1667-1675. 2017.
[3] Kosti, Ronak, Jose M. Alvarez, Adria Recasens, and Agata Lapedriza. "EMOTIC: Emotions in Context dataset." In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops, pp. 61-69. 2017.
