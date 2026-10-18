<div align="center">

# 🖼️ Distributed Image Processing Pipeline

**Масштабируемый распределенный программный комплекс конвейерной фильтрации и анализа цифровых изображений**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-Broker-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PyQt6](https://img.shields.io/badge/PyQt-6.6-41CD52?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)

</div>

---

## 📌 О проекте

Проект представляет собой распределенную сервис-ориентированную систему для параллельной конвейерной обработки пакетов изображений произвольного разрешения. Архитектура построена по паттерну **Claim Check**: бинарные графические данные изолированы в локальном файловом хранилище, а обмен между асинхронным API, распределенными воркерами и клиентом осуществляется через легковесные идентификаторы и токены брокера сообщений.

### 🌟 Ключевые возможности:
* **Асинхронный REST API (FastAPI):** Высокоскоростной прием пакетов изображений и неблокирующая отдача метаданных.
* **Распределенная очередь (Celery + Redis):** Балансировка вычислительной нагрузки, горизонтальное масштабирование и гарантия повторного выполнения упавших задач (`acks_late`).
* **Хранение состояний (PostgreSQL + SQLAlchemy):** Персистентный учет жизненного цикла каждого кадра (`pending` ➔ `processing` ➔ `completed` / `failed`).
* **Модульный OpenCV-конвейер:** Гибкое динамическое построение цепочек фильтров любой конфигурации.
* **Neo-Dark десктопный клиент (PyQt6):** Интерфейс управления конвейером с реактивным мониторингом статусов задач в реальном времени.

---

## 🏗️ Архитектура системы

```text
[ Desktop Client (PyQt6) ]
           │
           │ HTTP POST (Batch Upload) / GET (Polling Status)
           ▼
[ FastAPI Backend Gateway ] ──(Writes Metadata)──► [ PostgreSQL DB ]
           │                                            ▲
           │ Dispatches Task IDs                        │
           ▼                                            │ Updates
    [ Redis Broker ]                                    │ Status
           │                                            │
           ├──► [ Celery Worker 1 (OpenCV Core) ] ──────┤
           ├──► [ Celery Worker 2 (OpenCV Core) ] ──────┤
           └──► [ Celery Worker N (OpenCV Core) ] ──────┘
                         │
                         ▼
             [ Local Storage / Results ]

⚙️ Алгоритмический конвейер (OpenCV Engine)

Воркеры поддерживают динамическую сборку последовательностей из следующих атомарных операций компьютерного зрения:
Фильтр	Метод / Алгоритм	Назначение
denoise_nlmeans	Fast Non-Local Means Denoising	Удаление высокочастотного аддитивного шума с сохранением четких текстур.
denoise_gaussian	Двумерная свертка Гаусса	Линейное сглаживание и подавление зернистости.
grayscale	Преобразование BGR ➔ Grayscale	Редукция размерности и переход к анализу яркостного канала.
clahe	Contrast Limited Adaptive Histogram Eq.	Локальное выравнивание динамического диапазона контрастности.
kmeans	Цветовая квантизация K-Means	Кластеризация цветовых векторов и уменьшение размера палитры кадра.
canny	Детектор границ Кэнни	Вычисление градиента, подавление немаксимумов и гистерезисная фильтрация.
sobel	Оператор градиента Собеля	Вычисление первых производных функции яркости по осям X и Y.
📁 Структура проекта
code Text

image_pipeline_app/
├── client/                 # Десктоп-клиент PyQt6
│   ├── api_client.py       # Сетевой адаптер взаимодействия с API
│   ├── main_window.py      # Графический интерфейс Neo-Dark Dashboard
│   └── styles.py           # Таблица стилей QSS
├── server/                 # Серверная часть FastAPI
│   ├── main.py             # Точки входа API, контроллеры загрузки/выгрузки
│   └── schemas.py          # Модели валидации Pydantic
├── workers/                # Вычислительные узлы Celery
│   ├── celery_app.py       # Конфигурация брокера и параметров воркера
│   └── tasks.py            # Фоновые процедуры конвейерной обработки
├── database/               # Слой данных
│   ├── connection.py       # Движок и фабрика сессий SQLAlchemy
│   └── models.py           # Реляционная модель Task
├── pipelines/              # Математическое ядро компьютерного зрения
│   ├── filters.py          # Атомарные функции OpenCV/NumPy
│   └── executor.py         # Линейный исполнитель цепочки фильтров
├── storage/                # Локальное хранилище Claim Check
│   ├── uploads/            # Входящие пакеты
│   └── results/            # Обработанные файлы
├── config.py               # Глобальная конфигурация среды
├── run_client.py           # Скрипт запуска GUI-приложения
└── requirements.txt        # Зависимости Python

🚀 Инструкция по локальному развертыванию (без Docker)

Для демонстрации работы независимых сервисов распределенной системы используется несколько терминалов.
1. Системные службы

Убедитесь, что брокер Redis и СУБД PostgreSQL запущены в системе:
code Bash

sudo systemctl status redis-server
sudo systemctl status postgresql

2. Запуск серверных компонентов

Сервер FastAPI:
code Bash

cd ~/Labs/image_pipeline_app
source venv/bin/activate
uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload

Интерактивная документация Swagger UI доступна по адресу: http://127.0.0.1:8000/docs

Вычислительный воркер Celery:
code Bash

cd ~/Labs/image_pipeline_app
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info -c 4

Десктопный клиент PyQt6:
code Bash

cd ~/Labs/image_pipeline_app
source venv/bin/activate
python run_client.py

📜 Версионирование

    v0.1.0 — Каркас проекта, реляционные модели PostgreSQL и конфигурация.

    v0.2.0 — Алгоритмический конвейер OpenCV и класс PipelineExecutor.

    v0.3.0 — Интеграция брокера Redis и задач воркера Celery.

    v0.4.0 — REST API на FastAPI с поддержкой Claim Check.

    v0.5.0 — Реактивный десктопный клиент на PyQt6 в стиле Neo-Dark Dashboard.

    v0.5.1 — Документирование архитектуры, спецификации API и руководства запуска.
