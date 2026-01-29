# 🎵 Руководство по аналитике артистов

## 📋 Обзор

Система предоставляет два способа получения аналитики по артистам:

1. **REST API** - прямые HTTP запросы к эндпоинтам
2. **AI Агент** - естественный язык через `/query` эндпоинт

---

## 🔌 REST API

### База URL
```
http://localhost:8002/api/v1/artists
```

### Доступные эндпоинты

#### 1. Поиск артистов
```http
GET /api/v1/artists/search?query=Ernar&period=q3_2025&limit=20
```

**Параметры:**
- `query` (обязательный) - поисковый запрос
- `period` (опционально) - период данных: `q3_2025`, `q4_2025`, `all`
- `limit` (опционально) - максимум результатов (по умолчанию 20)

**Ответ:**
```json
{
  "query": "Ernar",
  "period": "q3_2025",
  "count": 2,
  "artists": [
    "Ernar Amandyq",
    "Ernar Kurmashev"
  ]
}
```

---

#### 2. Статистика стримов
```http
GET /api/v1/artists/Ernar%20Amandyq/streams?period=q3_2025
```

**Ответ:**
```json
{
  "total_streams": 9106857,
  "total_revenue": 2118.18,
  "average_per_stream": 0.000233,
  "period": "q3_2025"
}
```

---

#### 3. Статистика по платформам (DSP)
```http
GET /api/v1/artists/Ernar%20Amandyq/platforms?period=q3_2025&top_n=5
```

**Ответ:**
```json
{
  "artist": "Ernar Amandyq",
  "period": "q3_2025",
  "total_platforms": 25,
  "top_platforms": [
    {
      "platform": "Yandex",
      "streams": 4500000,
      "revenue": 850.50,
      "percentage": 40.15
    },
    {
      "platform": "Spotify",
      "streams": 2800000,
      "revenue": 620.30,
      "percentage": 29.28
    }
  ]
}
```

---

#### 4. География (демография)
```http
GET /api/v1/artists/Ernar%20Amandyq/geography?period=q3_2025&top_n=10
```

**Ответ:**
```json
{
  "artist": "Ernar Amandyq",
  "period": "q3_2025",
  "total_countries": 45,
  "top_countries": [
    {
      "country": "Kazakhstan",
      "streams": 6500000,
      "revenue": 1450.80,
      "percentage": 68.50
    },
    {
      "country": "Russian federation",
      "streams": 1800000,
      "revenue": 420.60,
      "percentage": 19.86
    }
  ]
}
```

---

#### 5. Статистика по трекам
```http
GET /api/v1/artists/Ernar%20Amandyq/tracks?period=q3_2025&top_n=5
```

**Ответ:**
```json
{
  "artist": "Ernar Amandyq",
  "period": "q3_2025",
  "total_tracks": 9,
  "top_tracks": [
    {
      "track_name": "Keipker",
      "streams": 5440707,
      "revenue": 1272.92,
      "percentage": 60.10
    },
    {
      "track_name": "Meni kut",
      "streams": 3217932,
      "revenue": 769.18,
      "percentage": 36.32
    }
  ]
}
```

---

#### 6. Полная аналитика
```http
GET /api/v1/artists/Ernar%20Amandyq/analytics?period=q3_2025&top_n=5
```

**Ответ:** Комбинированные данные всех предыдущих эндпоинтов.

---

## 🤖 AI Агент

### Использование через естественный язык

Отправляйте вопросы на русском языке через `/query` эндпоинт:

```http
POST /query
Content-Type: application/json

{
  "question": "Сколько стримов у Ernar Amandyq в Q3 2025?",
  "uuid": "user-123"
}
```

### Примеры вопросов

#### Поиск артистов
```
"Найди артистов с именем Ernar"
"Есть ли артист Yenlik?"
"Покажи всех артистов с 'Ghetto' в имени"
```

#### Стримы и доходы
```
"Сколько стримов у Ernar Amandyq?"
"Какой доход у Yenlik в Q3 2025?"
"Средняя цена за стрим для Darkhan Juzz"
```

#### Платформы (DSP)
```
"На каких платформах популярен Ernar Amandyq?"
"Топ-5 DSP для Yenlik"
"Где больше всего слушают Shiza?"
"Сколько Spotify приносит Ernar Amandyq?"
```

#### География
```
"В каких странах популярен Ernar Amandyq?"
"Топ-10 стран для Yenlik"
"Демография артиста Darkhan Juzz"
"Откуда больше всего слушателей у Shiza?"
```

#### Треки
```
"Какие самые популярные треки у Ernar Amandyq?"
"Топ-5 треков Yenlik по доходу"
"Сколько заработал трек Keipker?"
```

#### Комплексная аналитика
```
"Дай полную аналитику по Ernar Amandyq"
"Покажи все данные по Yenlik за Q3 2025"
"Полный отчет по артисту Darkhan Juzz"
```

---

## 📊 Периоды данных

- **`q3_2025`** - Июль, Август, Сентябрь 2025 (полный квартал)
- **`q4_2025`** - Октябрь, Ноябрь 2025 (неполный квартал, нет декабря)
- **`all`** - Все доступные данные (июль-ноябрь 2025)

---

## 🔧 Примеры использования

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8002/api/v1/artists"

# Поиск артиста
response = requests.get(f"{BASE_URL}/search", params={
    "query": "Ernar",
    "period": "q3_2025"
})
artists = response.json()["artists"]

# Получить стримы
artist_name = artists[0]
response = requests.get(f"{BASE_URL}/{artist_name}/streams", params={
    "period": "q3_2025"
})
streams_data = response.json()
print(f"Стримов: {streams_data['total_streams']:,}")
print(f"Доход: {streams_data['total_revenue']:.2f} EUR")

# Полная аналитика
response = requests.get(f"{BASE_URL}/{artist_name}/analytics", params={
    "period": "q3_2025",
    "top_n": 10
})
analytics = response.json()
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8002/api/v1/artists";

// Поиск артиста
const searchArtists = async (query) => {
  const response = await fetch(
    `${BASE_URL}/search?query=${encodeURIComponent(query)}&period=q3_2025`
  );
  return await response.json();
};

// Получить стримы
const getStreams = async (artistName) => {
  const response = await fetch(
    `${BASE_URL}/${encodeURIComponent(artistName)}/streams?period=q3_2025`
  );
  return await response.json();
};

// Использование
const artists = await searchArtists("Ernar");
const streams = await getStreams(artists.artists[0]);
console.log(`Стримов: ${streams.total_streams.toLocaleString()}`);
console.log(`Доход: ${streams.total_revenue.toFixed(2)} EUR`);
```

### cURL

```bash
# Поиск артиста
curl "http://localhost:8002/api/v1/artists/search?query=Ernar&period=q3_2025"

# Стримы
curl "http://localhost:8002/api/v1/artists/Ernar%20Amandyq/streams?period=q3_2025"

# Платформы
curl "http://localhost:8002/api/v1/artists/Ernar%20Amandyq/platforms?period=q3_2025&top_n=5"

# Полная аналитика
curl "http://localhost:8002/api/v1/artists/Ernar%20Amandyq/analytics?period=q3_2025"
```

---

## 🚀 Запуск сервера

```bash
# Активировать виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Запустить сервер
python -m uvicorn app.api:app --host 0.0.0.0 --port 8002 --reload
```

Сервер будет доступен по адресу: `http://localhost:8002`

Документация API (Swagger): `http://localhost:8002/docs`

---

## 📝 Доступные инструменты для AI агента

Агент автоматически выбирает нужный инструмент на основе вопроса:

1. **search_artists** - поиск артистов
2. **get_artist_streams** - статистика стримов
3. **get_artist_platforms** - статистика по DSP
4. **get_artist_geography** - география/демография
5. **get_artist_tracks** - статистика по трекам
6. **get_artist_full_analytics** - полная аналитика

---

## ⚠️ Примечания

- Все доходы указаны в **EUR**
- Данные актуальны на **26 января 2026**
- Поиск артистов **регистронезависимый**
- Имена артистов должны быть **точными** для получения статистики
- Q4 2025 содержит только октябрь и ноябрь (декабрь отсутствует)

---

## 🆘 Поддержка

При возникновении ошибок:
1. Проверьте правильность написания имени артиста через `/search`
2. Убедитесь, что выбран правильный период
3. Проверьте логи сервера для детальной информации

---

*Документация обновлена: 26 января 2026*

