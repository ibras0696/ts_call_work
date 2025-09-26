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

### Загрузка записи и обработка
```bash
# 1) создаём звонок
CALL_ID=$(curl -s -X POST "http://localhost:8000/calls/" \
  -H "Content-Type: application/json" \
  -d '{"caller":"+79001234567","receiver":"+79007654321","started_at":"2025-09-27T12:00:00Z"}' | jq -r .id)

# 2) загружаем .wav/.mp3
curl -s -X POST "http://localhost:8000/calls/$CALL_ID/recording" \
  -F "file=@/path/to/sample.wav" | jq .

# 3) дождитесь обработки воркером и проверьте
curl -s "http://localhost:8000/calls/$CALL_ID" | jq .
```

Ошибки:
- 422 unsupported_extension — не .mp3/.wav
- 409 recording_already_exists — повторная загрузка для того же call

## Дальше по ТЗ
- [x] POST /calls/{id}/recording (multipart, сохранение файла, задача Celery)
- [x] Worker: pydub duration, фейковый транскрипт, status=ready
- [ ] (опц.) поиск /calls?query=, download presigned URL
- [ ] Тесты pytest (happy path)
- [ ] ruff/mypy в CI
# ts_call_work
