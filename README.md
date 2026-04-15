# Link Shortener API

Сокращатель ссылок на FastAPI с асинхронным PostgreSQL.

### Docker (рекомендуется)
```bash
docker-compose up -d
```

### Локальный запуск
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Создание короткой ссылки
**POST** `/api/short-links`

**Параметры:**
- `long_url` (string, required) - оригинальная ссылка

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/short-links" \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com/very-long-url"}'
```

**Пример ответа:**
```json
{
  "short_link": "abc123"
}
```

### Редирект по короткой ссылке
**GET** `/api/short-links/{slug}`

**Параметры:**
- `slug` (string, path) - короткий идентификатор ссылки

**Пример:**
```
http://localhost:8000/api/short-links/abc123
```

## 🗄️ База данных

- **PostgreSQL 17** на порту 6432
- Таблица `links` с полями:
  - `slug` (primary key) - короткий идентификатор
  - `url` - оригинальная ссылка

## 📦 Конфигурация

### Docker
- **API**: порт 8000
- **БД**: порт 6432
- **Сеть**: docker-compose

### Переменные окружения
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=short_links
```

## 🛠️ Технологический стек

- **Backend**: FastAPI 0.135+
- **Database**: PostgreSQL 17 + SQLAlchemy 2.0
- **Async**: asyncpg + async/await
- **Container**: Docker + docker-compose
- **Python**: 3.12+

## 📝 Лицензия

MIT License