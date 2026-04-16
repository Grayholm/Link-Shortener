# Link Shortener API

Небольшой сервис сокращения ссылок на `FastAPI` с `PostgreSQL`, `Redis`, `SQLAlchemy` и `Alembic`.

## Что умеет

- Создаёт короткий `slug` для переданного URL.
- Редиректит по короткой ссылке на исходный адрес.
- Кэширует редиректы в `Redis`.
- Повторяет генерацию `slug`, если возникла коллизия в БД.
- Продолжает работать даже при недоступном `Redis`:
  редиректы будут идти через базу данных без кэша.

## Стек

- `Python 3.13+`
- `FastAPI`
- `SQLAlchemy 2.0`
- `asyncpg`
- `PostgreSQL`
- `Redis`
- `Alembic`
- `pytest` + `pytest-asyncio`
- `Docker` + `docker-compose`

## Структура проекта

```text
src/
  api.py                 # HTTP-роуты
  service.py             # бизнес-логика
  repository.py          # работа с БД
  dependencies.py        # FastAPI dependencies
  exceptions.py          # доменные ошибки
  main.py                # точка входа FastAPI
  scheme.py              # Pydantic-схемы запросов
  database/
    config.py            # настройки приложения и env
    db.py                # engine и sessionmaker
    redis_config.py      # клиент Redis
  migrations/            # Alembic-миграции
tests/
  unit_test.py
```

## Переменные окружения

Сервис читает настройки из файла `.env`.
Если переменные не заданы, будут использованы значения по умолчанию из `src/database/config.py`.

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=short_links
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

Для локального запуска без Docker обычно удобно указать, например:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=6432
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Быстрый старт через Docker

```bash
docker-compose up -d --build
```

После старта API будет доступно по адресу:

```text
http://localhost:8000
```

## Миграции

Применить все миграции:

```bash
alembic upgrade head
```

Если сервис поднят через Docker, миграции можно запускать из контейнера API или из локального окружения с корректными переменными окружения.

## Локальный запуск без Docker

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Поднять `PostgreSQL` и `Redis`.

3. Настроить `.env` под локальные хосты и порты.

4. Применить миграции:

```bash
alembic upgrade head
```

5. Запустить приложение:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API

### Создать короткую ссылку

`POST /api/short-links`

Тело запроса:

```json
{
  "long_url": "https://example.com/very-long-url"
}
```

Пример:

```bash
curl -X POST "http://localhost:8000/api/short-links" \
  -H "Content-Type: application/json" \
  -d "{\"long_url\":\"https://example.com/very-long-url\"}"
```

Успешный ответ:

```json
{
  "short_link": "abc123"
}
```

### Перейти по короткой ссылке

`GET /api/short-links/{slug}`

Пример:

```text
http://localhost:8000/api/short-links/abc123
```

Ответ:

`302 Found` с редиректом на исходный URL.

## Ошибки

Примеры ответов:

```json
{
  "detail": "Link not found"
}
```

```json
{
  "detail": "Link already exists"
}
```

## Тесты

Запуск тестов:

```bash
python -m pytest -q
```

Текущее покрытие unit-тестов включает:

- создание короткой ссылки;
- retry при коллизии `slug`;
- ошибку после исчерпания лимита retry;
- редирект по существующему `slug`;
- поведение при недоступном `Redis`.

## Docker-сервисы

`docker-compose.yml` поднимает:

- `api` на порту `8000`;
- `db` на порту `6432`;
- `redis` на порту `6379`.

## Что можно улучшить дальше

- Добавить API/integration тесты.
- Убрать `sys.path.append(...)` из `src/main.py`.
- Добавить healthcheck и readiness/liveness endpoints.
- Вынести уровень логирования и `echo=True` для SQLAlchemy в конфиг.
