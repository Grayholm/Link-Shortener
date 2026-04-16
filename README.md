# Link Shortener API

Небольшой сервис сокращения ссылок на `FastAPI` с `PostgreSQL`, `Redis` и асинхронным доступом к данным.

## Что умеет

- Создает короткую ссылку для переданного URL.
- Ищет оригинальный URL по `slug`.
- Кэширует редиректы в `Redis`.
- Обрабатывает доменные ошибки через общий `FastAPI` exception handler.

## Стек

- `Python 3.13+`
- `FastAPI`
- `SQLAlchemy 2.0`
- `asyncpg`
- `PostgreSQL 17`
- `Redis 7`
- `Alembic`
- `pytest` + `pytest-asyncio`
- `Docker` + `docker-compose`

## Структура проекта

```text
src/
  api.py            # HTTP-роуты
  service.py        # бизнес-логика
  repository.py     # работа с БД
  db.py             # engine и sessionmaker
  redis_config.py   # подключение к Redis
  exceptions.py     # доменные ошибки приложения
  main.py           # FastAPI app и общий handler ошибок
  scheme.py         # Pydantic-схемы
  migrations/       # Alembic-миграции
tests/
  unit_test.py
```

## Быстрый старт

Рекомендуемый способ запуска: через `docker-compose`, потому что текущая конфигурация приложения ожидает сервисы БД и Redis по хостам `db` и `redis`.

```bash
docker-compose up -d --build
```

После старта API будет доступно по адресу:

```text
http://localhost:8000
```

## Миграции

Если база поднята, применить миграции можно так:

```bash
alembic upgrade head
```

## Локальный запуск без Docker

Если хочешь запускать приложение локально, установи зависимости:

```bash
pip install -r requirements.txt
```

Затем подними отдельно `PostgreSQL` и `Redis` и убедись, что приложение может достучаться до хостов, указанных в коде:

- БД: `db:5432`
- Redis: `redis:6379`

После этого можно запускать сервер:

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

Ответом будет `302 Redirect` на исходный URL.

## Ошибки

Приложение использует базовую ошибку `AppError` и общий обработчик в `FastAPI`.

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

Текущие unit-тесты покрывают:

- создание короткой ссылки;
- обработку конфликта при генерации;
- получение оригинального URL;
- кэширование редиректа через `Redis`.

## Docker

Сервисы из `docker-compose.yml`:

- `api` на порту `8000`
- `db` на порту `6432`
- `redis` на порту `6379`

## Что можно улучшить дальше

- Вынести настройки БД и Redis в переменные окружения.
- Добавить интеграционные тесты для API.
- Расширить локальную конфигурацию без привязки к Docker-хостам.

## Лицензия

MIT
