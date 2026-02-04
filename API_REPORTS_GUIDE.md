# 📊 API для работы с PDF-отчетами

## 🎯 Два способа генерации отчетов

### 1️⃣ Через AI-агента (`/query`) ⭐ Рекомендуется

**Естественный язык** - просто спросите:

```bash
POST /query
{
  "question": "Сделай отчет для артиста Darkhan Juzz"
}
```

**Ответ:**
```json
{
  "answer": "✅ PDF-отчет успешно создан для артиста Darkhan Juzz\n\n📥 Скачать: /reports/download/Darkhan_Juzz_Report_20260204_173424.pdf",
  "tool_used": "generate_artist_report",
  "tool_parameters": {
    "artist_name": "Darkhan Juzz"
  }
}
```

---

### 2️⃣ Прямой API endpoint (`/reports/generate`)

**Программный доступ** - для интеграций:

```bash
POST /reports/generate
{
  "artist_name": "Darkhan Juzz",
  "period": "Q4 2025",
  "include_medialand": false
}
```

**Ответ:**
```json
{
  "success": true,
  "artist_name": "Darkhan Juzz",
  "pdf_filename": "Darkhan_Juzz_Report_20260204_173424.pdf",
  "pdf_url": "/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf",
  "summary": "📊 Основные показатели:\n- Всего стримов: 7,353,152\n...",
  "message": "✅ PDF-отчет успешно создан"
}
```

---

## 📥 Скачивание отчетов

### GET `/reports/download/{filename}`

Скачивает PDF-файл:

```bash
GET /reports/download/Darkhan_Juzz_Report_20260204_173424.pdf
```

**Возвращает:** PDF файл для скачивания

**В браузере:**
```
http://localhost:8002/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf
```

**С помощью curl:**
```bash
curl -O http://localhost:8002/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf
```

**С помощью Python:**
```python
import requests

url = "http://localhost:8002/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf"
response = requests.get(url)

with open("report.pdf", "wb") as f:
    f.write(response.content)
```

---

## 📋 Список всех отчетов

### GET `/reports/list`

Получить список всех сгенерированных отчетов:

```bash
GET /reports/list
```

**Ответ:**
```json
{
  "success": true,
  "reports": [
    {
      "filename": "Darkhan_Juzz_Report_20260204_173424.pdf",
      "artist_name": "Darkhan Juzz",
      "download_url": "/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf",
      "size_bytes": 145234,
      "size_mb": 0.14,
      "created_at": "2026-02-04T17:34:24"
    }
  ],
  "total_count": 3,
  "total_size_mb": 0.42
}
```

---

## ℹ️ Информация об отчете

### GET `/reports/info/{filename}`

Получить метаданные конкретного отчета:

```bash
GET /reports/info/Darkhan_Juzz_Report_20260204_173424.pdf
```

**Ответ:**
```json
{
  "success": true,
  "filename": "Darkhan_Juzz_Report_20260204_173424.pdf",
  "artist_name": "Darkhan Juzz",
  "download_url": "/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf",
  "path": "/path/to/reports/artist_reports/Darkhan_Juzz_Report_20260204_173424.pdf",
  "size_bytes": 145234,
  "size_mb": 0.14,
  "created_at": "2026-02-04T17:34:24"
}
```

---

## 🗑️ Удаление отчета

### DELETE `/reports/delete/{filename}`

Удалить отчет:

```bash
DELETE /reports/delete/Darkhan_Juzz_Report_20260204_173424.pdf
```

**Ответ:**
```json
{
  "success": true,
  "message": "Report 'Darkhan_Juzz_Report_20260204_173424.pdf' deleted successfully"
}
```

---

## 🔀 Выбор подхода: Хранить или отдавать?

### ✅ **Текущее решение: Хранить на сервере** (Рекомендуется)

**Преимущества:**
1. ✅ Можно **скачать позже** (ссылка всегда доступна)
2. ✅ **История отчетов** - видно все сгенерированные
3. ✅ **Кэширование** - не генерировать повторно
4. ✅ **Делиться ссылками** - просто отправить URL
5. ✅ Работает через `/query` (естественный язык)

**Недостатки:**
- ⚠️ Занимает место на диске (~150KB на отчет)
- 🔧 Нужна периодическая очистка старых файлов

---

### 🔄 **Альтернатива: Отдавать файл сразу**

Если нужно отдавать PDF напрямую в ответе (без хранения):

```python
# В reports.py можно добавить:
@router.post("/generate-and-download")
async def generate_and_download(request: GenerateReportRequest):
    # Генерируем в temp
    # Отдаем FileResponse
    # Удаляем файл
    ...
    return FileResponse(temp_pdf_path, filename="report.pdf")
```

**Когда использовать:**
- Нужен одноразовый отчет (без истории)
- Экономия места на диске
- Нет необходимости в повторном скачивании

---

## 📁 Структура хранения

```
reports/
  artist_reports/
    Darkhan_Juzz_Report_20260204_173424.pdf
    Yenlik_Report_20260204_173425.pdf
    Mona_Songz_Report_20260204_173426.pdf
    ...
```

**Формат имени:**
```
{Artist_Name}_Report_{Timestamp}.pdf
```

**Пример:**
- `Darkhan_Juzz_Report_20260204_173424.pdf`
- Артист: Darkhan Juzz
- Дата создания: 2026-02-04 17:34:24

---

## 🔒 Безопасность

### Защита от path traversal:

```python
# Автоматическая проверка в API:
if '..' in filename or '/' in filename or '\\' in filename:
    raise HTTPException(status_code=400, detail="Invalid filename")
```

### Ограничения:
- Только `.pdf` файлы
- Только из папки `reports/artist_reports/`
- Нет доступа к другим директориям

---

## 💡 Примеры использования

### JavaScript/TypeScript (Frontend):

```typescript
// Генерация через AI-агента
const response = await fetch('/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Сделай отчет для артиста Darkhan Juzz"
  })
});
const result = await response.json();

// Извлекаем URL для скачивания
const downloadUrl = result.tool_parameters?.download_url;

// Скачивание
window.open(downloadUrl, '_blank');
```

### Python:

```python
import requests

# Вариант 1: Через AI-агента
response = requests.post('http://localhost:8002/query', json={
    'question': 'Сделай отчет для артиста Darkhan Juzz'
})
result = response.json()
print(result['answer'])

# Вариант 2: Прямой API
response = requests.post('http://localhost:8002/reports/generate', json={
    'artist_name': 'Darkhan Juzz',
    'period': 'Q4 2025'
})
data = response.json()

# Скачать PDF
pdf_response = requests.get(f"http://localhost:8002{data['pdf_url']}")
with open('report.pdf', 'wb') as f:
    f.write(pdf_response.content)
```

### cURL:

```bash
# Генерация через AI
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Сделай отчет для артиста Darkhan Juzz"}'

# Прямая генерация
curl -X POST http://localhost:8002/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Darkhan Juzz"}'

# Скачивание
curl -O http://localhost:8002/reports/download/Darkhan_Juzz_Report_20260204_173424.pdf

# Список отчетов
curl http://localhost:8002/reports/list

# Удаление
curl -X DELETE http://localhost:8002/reports/delete/Darkhan_Juzz_Report_20260204_173424.pdf
```

---

## 🧹 Автоматическая очистка (опционально)

Для автоматического удаления старых отчетов можно добавить:

```python
# В reports.py
@router.post("/cleanup")
async def cleanup_old_reports(days_old: int = 30):
    """Delete reports older than X days"""
    # Реализация очистки
    ...
```

---

## 📊 Swagger UI

Все endpoints доступны в Swagger UI:

```
http://localhost:8002/docs
```

Разделы:
- **reports** - генерация и управление отчетами
- **query** - AI-агент (использует reports под капотом)

---

## ✅ Итог: Рекомендованный workflow

### Для пользователей (UI):

```
1. Спрашивают через чат: "Сделай отчет для Darkhan Juzz"
2. AI вызывает тулу generate_artist_report
3. Получают ссылку для скачивания
4. Могут скачать позже из истории (/reports/list)
```

### Для разработчиков (API):

```
1. POST /reports/generate
2. Получают download_url
3. GET /reports/download/{filename}
4. Сохраняют PDF локально
```

**Оба подхода работают одновременно!** 🎉

