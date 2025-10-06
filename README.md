# Calls Service 📞⚡
Микросервис для управления звонками и записями: приём метаданных, загрузка аудио, асинхронная обработка, хранение в Postgres, маршрутизация через FastAPI и фоновые задачи в Celery.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-async-8C2728">
  <img alt="Alembic" src="https://img.shields.io/badge/Alembic-migrations-444">
  <img alt="Celery" src="https://img.shields.io/badge/Celery-5.x-37814A?logo=celery&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white">
  <img alt="pydub" src="https://img.shields.io/badge/pydub%20%2B%20ffmpeg-audio-555">
  <img alt="Lint" src="https://img.shields.io/badge/ruff-lint-0A7BBB">
  <img alt="Types" src="https://img.shields.io/badge/mypy-strict-2A6DB2">
  <img alt="Tests" src="https://img.shields.io/badge/pytest-ready-0A9EDC?logo=pytest&logoColor=white">
</p>

— Архитектурно: FastAPI + SQLAlchemy (async) + Alembic + Celery + Redis + PostgreSQL.  
— Практики: строгая типизация, слои, DTO, миграции, Docker, dev-зависимости и статанализ.

---

## Содержание
- Что делает сервис
- Архитектура и модель данных
- API эндпоинты
- Установка и запуск (локально и в Docker)
- Переменные окружения
- Миграции Alembic
- Тесты и качество кода
- Структура проекта

---

## Что делает сервис
- Создаёт сущность Call (звонок) с базовыми метаданными.
- Принимает запись разговора (multipart upload) и сохраняет файл на диск.
- Запускает фоновую обработку записи (Celery task), где можно считать длительность, тишину, базовый транскрипт и т.п.
- Сохраняет результаты в сущности Recording и даёт ссылку на скачивание (через presigned URL при включённой S3-конфигурации).

Статусы звонка: created → processing → ready.

---

## Архитектура (высокоуровнево)
```mermaid
flowchart LR
  Client -->|HTTP| API[FastAPI]
  API --> AppServices[Application/Services]
  AppServices --> DB[(PostgreSQL)]
  AppServices --> FS[(Recordings volume)]
  API -->|enqueue| Celery[Celery Worker]
  Celery --> FS
  Celery --> DB
```

- API: FastAPI роуты `/calls` и `/calls/{id}/recording`
- БД: SQLAlchemy (async) + Alembic
- Очередь: Celery (Redis broker/backend)
- Файлы: локальный том (директория RECORDINGS_DIR)
- Опционально: выдача presigned URL (S3/MinIO)

---

## Модель данных (главное)
- Call
  - id (UUID), caller, receiver, started_at, status
  - created_at, updated_at
  - one-to-one: Recording
- Recording
  - id (UUID), call_id (unique)
  - filename, duration_sec?, transcription?, silence_marks? (JSON)
  - created_at, updated_at

См. [app/models/call.py](app/models/call.py) и [app/models/recording.py](app/models/recording.py).

---

## API эндпоинты
Быстрые интерактивные доки: /docs и /redoc (FastAPI).

- POST /calls
  - Тело (JSON): caller, receiver, started_at (ISO8601)
  - Ответ: CallOut (id, caller, receiver, started_at, status, created_at, updated_at)
- GET /calls/{call_id}
  - Возвращает CallOut, 404 если не найден
- GET /calls
  - query (строка, min 2), limit (1..200), offset (>=0)
  - Ответ: { total, items: CallOut[] }
- POST /calls/{call_id}/recording
  - multipart/form-data: file=@audio.wav
  - Сохраняет файл, создаёт запись Recording, публикует Celery-задачу
  - Ошибки: 409 (если уже есть запись), 422 (неподдерживаемое расширение)
- GET /calls/{call_id}/download
  - Возвращает { url } с presigned ссылкой (при включённом S3), иначе 501

Примеры:
```bash
# 1) Создать звонок
curl -sX POST http://localhost:8000/calls \
  -H "Content-Type: application/json" \
  -d '{"caller":"+79001234567","receiver":"+79007654321","started_at":"2025-09-27T20:00:00Z"}'

# 2) Загрузить запись (multipart)
CALL_ID=<uuid>
curl -sX POST "http://localhost:8000/calls/$CALL_ID/recording" \
  -F "file=@./sample.wav"

# 3) Поиск
curl -s "http://localhost:8000/calls?query=+7900&limit=10&offset=0"
```

---

## Установка и запуск

Требования:
- Python 3.12
- FFmpeg (для pydub)
- PostgreSQL, Redis

### Вариант A: локально
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip

# Установка пакета и dev-инструментов из pyproject.toml
pip install -e .[dev]

# Экспорт переменных окружения или создайте .env (см. ниже)
export DATABASE_URL="postgresql+asyncpg://app:app@localhost:5432/calls"
export REDIS_URL="redis://localhost:6379/0"
export RECORDINGS_DIR="./recordings"

# Миграции
alembic upgrade head

# Запуск API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запуск Celery-воркера (автодискавер задач настроен на пакет app)
celery -A app.core.celery_app.celery_app worker -l info
```

Поднять инфраструктуру быстро (пример):
```bash
# Redis
docker run -d --name redis -p 6379:6379 redis:7

# PostgreSQL
docker run -d --name pg \
  -e POSTGRES_PASSWORD=app -e POSTGRES_USER=app -e POSTGRES_DB=calls \
  -p 5432:5432 postgres:16
```

Важно: установите FFmpeg локально (например, `brew install ffmpeg` на macOS, `sudo apt-get install ffmpeg` на Debian/Ubuntu).

### Вариант B: Docker
См. [Dockerfile](Dockerfile). Пример:
```bash
docker build -t calls-service .
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://app:app@host.docker.internal:5432/calls" \
  -e REDIS_URL="redis://host.docker.internal:6379/0" \
  -e RECORDINGS_DIR="/recordings" \
  -v "$(pwd)/recordings:/recordings" \
  calls-service
```

---

## Переменные окружения (.env)
См. [app/core/config.py](app/core/config.py). Ключевые переменные:
- DATABASE_URL — строка подключения SQLAlchemy async, например:
  `postgresql+asyncpg://app:app@localhost:5432/calls`
- REDIS_URL — адрес брокера/бэкенда Celery, например:
  `redis://localhost:6379/0`
- RECORDINGS_DIR — директория для сохранения аудио
- Опционально S3/MinIO для presigned URL:
  - S3_ENABLED (bool), S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET, S3_REGION, S3_SECURE

Пример .env:
```env
APP_ENV=dev
APP_NAME=CallsService

DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/calls
REDIS_URL=redis://localhost:6379/0
RECORDINGS_DIR=./recordings

S3_ENABLED=false
# S3_ENDPOINT_URL=http://localhost:9000
# S3_ACCESS_KEY=...
# S3_SECRET_KEY=...
# S3_BUCKET=calls
# S3_REGION=us-east-1
# S3_SECURE=false
```

---

## Миграции Alembic
Проект включает Alembic-конфигурацию (см. `alembic.ini`, `migrations/`).
```bash
# создать новую ревизию (автогенерация по моделям)
alembic revision --autogenerate -m "init schema"

# применить миграции
alembic upgrade head

# откат
alembic downgrade -1
```

---

## Тесты и качество кода
Dev-зависимости: pytest, httpx, mypy (strict), ruff.

Команды:
```bash
pytest -q
ruff check .
mypy .
```

Опционально pre-commit:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Структура проекта (основное)
```
app/
  api/
    routes/
      calls.py         # CRUD/поиск, presigned download
      recordings.py    # загрузка файла записи
    deps.py            # зависимости FastAPI (DB-сессия и т.д.)
  core/
    config.py          # конфиг через pydantic-settings
    db.py              # SQLAlchemy async engine/session + Base
    celery_app.py      # Celery app и конфиг
  models/
    call.py            # Call, CallStatus
    recording.py       # Recording
  services/
    calls.py           # бизнес-операции по Call
    recordings.py      # операции по Recording
    storage.py         # сохранение файлов, presigned URL
  main.py              # точка входа FastAPI
migrations/            # Alembic env + версии
alembic.ini
pyproject.toml
Dockerfile
```
