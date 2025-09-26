# Calls Service (Test Assignment)

## Быстрый старт
```bash
cp .env.example .env
docker compose up -d --build
# дождитесь healthcheck БД
docker compose exec api alembic upgrade head
```

## Проверка
Создать звонок:
```bash
curl -s -X POST "http://localhost:8000/calls/" \
  -H "Content-Type: application/json" \
  -d '{
    "caller": "+79001234567",
    "receiver": "+79007654321",
    "started_at": "2025-09-26T12:00:00Z"
  }' | jq .
```
Вернуть по id:
```bash
curl -s http://localhost:8000/calls/<uuid> | jq .
```

## Дальше по ТЗ
- [ ] POST /calls/{id}/recording (multipart, сохранение файла, задача Celery)
- [ ] Worker: pydub duration, фейковый транскрипт, status=ready
- [ ] (опц.) поиск /calls?query=, download presigned URL
- [ ] Тесты pytest (happy path)
- [ ] ruff/mypy в CI
# ts_call_work
