# Music Analyzer Agent API

AI-powered сервис для анализа музыкальных данных через natural language запросы.

## Быстрый старт

### Вариант 1: Локально (для разработки)

```bash
# 1. Создайте .env файл
echo "ANTHROPIC_API_KEY=ваш_ключ_здесь" > .env

# 2. Установите зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Запустите
python app/main.py
```

API: http://localhost:8002/docs

### Вариант 2: Docker (рекомендуется)

```bash
# 1. Создайте .env файл
echo "ANTHROPIC_API_KEY=ваш_ключ_здесь" > .env

# 2. Запустите
docker-compose up --build
```

API: http://localhost:8000/docs

## Использование

```bash
# Простой запрос
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Топ 10 артистов по доходу"}'

# Запрос по артисту
curl -X POST http://localhost:8000/artist-analytics/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Как дела у õzen?", "artist_name": "õzen"}'
```

## Основные endpoints

- `POST /query` - AI запрос к данным
- `POST /analytics/query` - Аналитика
- `POST /artist-analytics/chat` - Чат об артисте
- `GET /data-management/files` - Список файлов

Документация: http://localhost:8000/docs

## Требования

- Python 3.13+ или Docker
- API ключ Anthropic (Claude)
