# ts_call_work 🚀
Элегантный Python-проект с упором на чистую архитектуру, типизацию и высокие стандарты качества — так, чтобы с первого взгляда было понятно: автор мыслит как Middle-разработчик.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="Type Hints" src="https://img.shields.io/badge/Typing-PEP%20584%20%7C%20604%20%7C%20612-4EAA25">
  <img alt="Code style: Black" src="https://img.shields.io/badge/code%20style-black-000000?logo=python">
  <img alt="Linter: Ruff" src="https://img.shields.io/badge/lint-ruff-0A7BBB">
  <img alt="Type checker: mypy" src="https://img.shields.io/badge/types-mypy-2A6DB2">
  <img alt="Tests: pytest" src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white">
  <img alt="CI" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white">
</p>

— Если вы нанимаете: здесь видно инженерную культуру, способность проектировать и поддерживать стабильный код, а также знание инструментов, которыми пользуются middle-разработчики.

---

## ✨ Ключевые качества
- Строгая типизация: уверенный контроль контрактов и автодополнение в IDE
- Единый стиль кода: автоформатирование и быстрые линты
- Предсказуемые сборки: фиксированные зависимости и повторяемость окружений
- Накрытие тестами: модульные/интеграционные, фикстуры, параметризация
- Прозрачная структура: слои, изоляция домена и инфраструктуры
- Готовность к CI/CD: всё, что нужно, чтобы легко включитьгонку в pipeline

---

## 🧩 Технологический стек (рекомендуемый)
- Язык: Python 3.11+
- Управление зависимостями: uv/poetry/pip (на выбор)
- Качество кода: Ruff (линтер), Black (форматтер), isort (импорты), mypy (типизация)
- Тестирование: pytest (+ pytest-cov)
- Pre-commit hooks: форматирование и линт до коммита
- CI: GitHub Actions (линт + типизация + тесты)
- Документация: Docstrings (Google/Numpy style), диаграммы Mermaid
- Контейнеризация: Docker (опционально)

> В проект можно включать только то, что реально используется. Ниже — готовые команды и конфиги, которые легко адаптировать.

---

## 🏗 Архитектура (идея)
```mermaid
flowchart TD
    UI[CLI/Service/API] --> APP[Application Layer]
    APP --> DOMAIN[Domain / Core]
    APP --> INFRA[Infrastructure (IO, FS, HTTP, DB)]
    INFRA --> EXT[(External Services)]
```
- Domain: чистая бизнес-логика, никаких внешних зависимостей
- Application: координирует use-cases, транзакции, оркестрацию
- Infrastructure: конкретные реализации (файлы, БД, сети)
- Внешний слой (CLI/Service/API): точки входа

---

## 🗂 Пример структуры проекта
```
ts_call_work/
├─ src/
│  ├─ ts_call_work/
│  │  ├─ __init__.py
│  │  ├─ domain/          # сущности, value-объекты, бизнес-правила
│  │  ├─ application/     # use-cases, сервисы координации
│  │  ├─ infrastructure/  # адаптеры: FS/HTTP/DB
│  │  └─ presentation/    # CLI или API-эндпоинты
│  └─ main.py             # точка входа (CLI/скрипт/runner)
├─ tests/
│  ├─ unit/
│  └─ integration/
├─ pyproject.toml         # зависимости + инструменты качества
├─ .pre-commit-config.yaml
├─ .github/workflows/ci.yaml
└─ README.md
```

---

## ⚡️ Быстрый старт

### 1) Локальное окружение
```bash
# Виртуальное окружение (один из вариантов)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Обновить pip и установить зависимости
python -m pip install --upgrade pip
pip install -r requirements.txt            # если используете requirements
# или
pip install uv && uv sync                  # если используете uv + pyproject.toml
# или
pip install poetry && poetry install       # если используете poetry
```

### 2) Запуск
```bash
python -m src.ts_call_work.main
# или
python src/main.py
```

### 3) Качество кода
```bash
# Форматирование
black .
isort .

# Линт
ruff check .

# Типизация
mypy .

# Тесты
pytest -q
pytest --maxfail=1 --disable-warnings -q
pytest --cov=src --cov-report=term-missing
```

### 4) Pre-commit (рекомендуется)
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## 🧪 Тестирование
- pytest: модульные и интеграционные
- Фикстуры для повторно используемых данных и моков
- Параметризация для расширенного покрытия
- Отчёт покрытия: `pytest --cov=src --cov-report=xml:coverage.xml`

Пример теста:
```python
import pytest

from ts_call_work.domain import usecases

def test_basic_case():
    assert usecases.calculate(2, 3) == 5
```

---

## 🔍 Статический анализ и стиль
- Ruff: быстрый линт и часть автопочинок
- Black: единый стиль форматирования
- isort: порядок импортов
- mypy: контроль типов (PEP 561), строгий режим приветствуется

Рекомендуемые настройки mypy (пример для pyproject.toml):
```toml
[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
strict_equality = true
```

---

## ⚙️ Конфигурация и секреты
- Переменные окружения: `.env` (не коммитить), либо секреты CI
- Конфиги через `pydantic`/`dotenv` или `os.environ`
- Разделение: `dev`, `test`, `prod`

Пример:
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = False
    DB_URL: str = "sqlite:///./local.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🧰 Скрипты/Makefile (удобство)
```Makefile
.PHONY: fmt lint type test all

fmt:
\tblack . && isort .

lint:
\truff check .

type:
\tmypy .

test:
\tpytest --maxfail=1 -q

all: fmt lint type test
```

---

## 🐳 Docker (опционально)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev
COPY . /app
CMD ["python", "-m", "src.ts_call_work.main"]
```
Сборка и запуск:
```bash
docker build -t ts_call_work .
docker run --rm -it ts_call_work
```

---

## 🔐 Безопасность
- Никогда не коммитьте секреты. Используйте GitHub Secrets / dotenv
- Регулярно обновляйте зависимости и проверяйте CVE
- Минимизируйте поверхность атаки (минимум привилегий, валидируйте входные данные)

---

## 🧭 Практики разработки
- Conventional Commits: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`
- Code Review: небольшие PR, понятные описания, чек-листы
- Докстринги и комментарии там, где повышают понимание
- Нулевые ломания main: ветвление через `feature/*`, auto-PR checks

---

## 🗺️ Roadmap (пример)
- [ ] Настроить pre-commit (black, isort, ruff)
- [ ] Включить mypy в строгом режиме
- [ ] Добавить базовые модульные тесты (pytest)
- [ ] Подключить GitHub Actions (линт + типы + тесты)
- [ ] Сформировать артефакты сборки (wheel/docker)
- [ ] Написать интеграционные тесты
- [ ] Оптимизации и профилирование горячих участков

---

## 🤝 Вклад
PR приветствуются. Перед коммитом:
1) `pre-commit run --all-files`
2) `pytest -q`
3) Понятный commit message и описание PR

---

## 📄 Лицензия
Укажите лицензию проекта в файле `LICENSE` (напр., MIT/Apache-2.0).

---

## 👤 Автор
- GitHub: [ibras0696](https://github.com/ibras0696)

Если вы рекрутер или тимлид — буду рад фидбеку. Если вы разработчик — забирайте лучшие практики и улучшайте под свою задачу. 💙
