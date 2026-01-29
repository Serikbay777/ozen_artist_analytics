# Data Management API

API для управления CSV файлами в каталоге `data/processed`.

## Базовый URL
```
http://localhost:8000/data
```

## Эндпоинты

### 1. Загрузка одного CSV файла

**POST** `/data/upload-csv`

Загружает один CSV файл в директорию `data/processed`.

#### Параметры
- `file` (file, required): CSV файл для загрузки

#### Пример запроса (curl)
```bash
curl -X POST "http://localhost:8000/data/upload-csv" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.csv"
```

#### Пример ответа (Success)
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "filename": "ozen_20260129_143522.csv",
  "original_filename": "ozen.csv",
  "path": "/Users/user/project/data/processed/ozen_20260129_143522.csv",
  "rows": 6225,
  "columns": [
    "Reporting Period",
    "Reporting Date",
    "Sale Month",
    "Country of Sale",
    "Store",
    "Artist",
    "Title",
    "Label",
    "Quantity",
    "Partner Share",
    "Currency",
    "Sale Type"
  ],
  "size_bytes": 1048576,
  "size_mb": 1.0
}
```

#### Особенности
- Файл автоматически переименовывается с добавлением timestamp для избежания конфликтов
- Возвращает метаданные: количество строк, список колонок, размер файла
- Принимает только CSV файлы

---

### 2. Пакетная загрузка CSV файлов

**POST** `/data/upload-csv-batch`

Загружает несколько CSV файлов одновременно.

#### Параметры
- `files` (files[], required): Список CSV файлов для загрузки

#### Пример запроса (curl)
```bash
curl -X POST "http://localhost:8000/data/upload-csv-batch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/file1.csv" \
  -F "files=@/path/to/file2.csv" \
  -F "files=@/path/to/file3.csv"
```

#### Пример ответа
```json
{
  "success": true,
  "total": 3,
  "uploaded_count": 3,
  "failed_count": 0,
  "uploaded": [
    {
      "filename": "file1_20260129_143522.csv",
      "original_filename": "file1.csv",
      "path": "/path/to/data/processed/file1_20260129_143522.csv",
      "rows": 1000,
      "columns": ["col1", "col2", "col3"],
      "size_bytes": 50000,
      "size_mb": 0.05
    },
    {
      "filename": "file2_20260129_143523.csv",
      "original_filename": "file2.csv",
      "path": "/path/to/data/processed/file2_20260129_143523.csv",
      "rows": 2000,
      "columns": ["col1", "col2"],
      "size_bytes": 75000,
      "size_mb": 0.07
    }
  ],
  "failed": []
}
```

---

### 3. Список всех файлов

**GET** `/data/list-files`

Возвращает список всех CSV файлов в директории `data/processed`.

#### Пример запроса (curl)
```bash
curl -X GET "http://localhost:8000/data/list-files" \
  -H "accept: application/json"
```

#### Пример ответа
```json
{
  "success": true,
  "files": [
    {
      "filename": "ozen_20260129_143522.csv",
      "path": "/path/to/data/processed/ozen_20260129_143522.csv",
      "size_bytes": 1048576,
      "size_mb": 1.0,
      "modified_at": "2026-01-29T14:35:22",
      "rows": 6225,
      "columns": 12
    },
    {
      "filename": "older_file_20260128_120000.csv",
      "path": "/path/to/data/processed/older_file_20260128_120000.csv",
      "size_bytes": 524288,
      "size_mb": 0.5,
      "modified_at": "2026-01-28T12:00:00",
      "rows": 3000,
      "columns": 8
    }
  ],
  "total_count": 2,
  "total_size_mb": 1.5
}
```

#### Особенности
- Файлы отсортированы по дате изменения (новые сверху)
- Показывает количество строк и колонок для каждого файла
- Показывает общий размер всех файлов

---

### 4. Информация о файле

**GET** `/data/file-info/{filename}`

Возвращает подробную информацию о конкретном CSV файле, включая превью первых 5 строк.

#### Параметры
- `filename` (path, required): Имя файла

#### Пример запроса (curl)
```bash
curl -X GET "http://localhost:8000/data/file-info/ozen_20260129_143522.csv" \
  -H "accept: application/json"
```

#### Пример ответа
```json
{
  "success": true,
  "filename": "ozen_20260129_143522.csv",
  "path": "/path/to/data/processed/ozen_20260129_143522.csv",
  "size_bytes": 1048576,
  "size_mb": 1.0,
  "modified_at": "2026-01-29T14:35:22",
  "rows": 6225,
  "columns": [
    "Reporting Period",
    "Reporting Date",
    "Sale Month",
    "Country of Sale",
    "Store",
    "Artist",
    "Title",
    "Label",
    "Quantity",
    "Partner Share",
    "Currency",
    "Sale Type"
  ],
  "column_count": 12,
  "data_types": {
    "Reporting Period": "object",
    "Reporting Date": "object",
    "Sale Month": "object",
    "Country of Sale": "object",
    "Store": "object",
    "Artist": "object",
    "Title": "object",
    "Label": "object",
    "Quantity": "int64",
    "Partner Share": "float64",
    "Currency": "object",
    "Sale Type": "object"
  },
  "preview": [
    {
      "Reporting Period": "2019 Q2",
      "Reporting Date": "2019-06-30",
      "Sale Month": "2019-04",
      "Country of Sale": "RU",
      "Store": "Spotify",
      "Artist": "õzen",
      "Title": "Track Name",
      "Label": "Label Name",
      "Quantity": 1000,
      "Partner Share": 5.5,
      "Currency": "EUR",
      "Sale Type": "Stream"
    }
    // ... ещё 4 строки
  ],
  "statistics": {
    "Quantity": {
      "min": 1,
      "max": 50000,
      "mean": 1234.5,
      "median": 500
    },
    "Partner Share": {
      "min": 0.001,
      "max": 500.0,
      "mean": 10.5,
      "median": 5.2
    }
  }
}
```

#### Особенности
- Показывает типы данных для каждой колонки
- Предоставляет превью первых 5 строк
- Для числовых колонок показывает статистику (min, max, mean, median)

---

### 5. Удаление файла

**DELETE** `/data/delete-file/{filename}`

Удаляет CSV файл из директории `data/processed`.

#### Параметры
- `filename` (path, required): Имя файла для удаления

#### Пример запроса (curl)
```bash
curl -X DELETE "http://localhost:8000/data/delete-file/old_file_20260101_120000.csv" \
  -H "accept: application/json"
```

#### Пример ответа
```json
{
  "success": true,
  "message": "File 'old_file_20260101_120000.csv' deleted successfully"
}
```

#### Особенности
- Безопасность: не позволяет удалять файлы за пределами директории `data/processed`
- Возвращает 404 если файл не найден

---

## Примеры использования

### Python (requests)

```python
import requests

# Загрузка файла
with open('mydata.csv', 'rb') as f:
    files = {'file': ('mydata.csv', f, 'text/csv')}
    response = requests.post('http://localhost:8000/data/upload-csv', files=files)
    print(response.json())

# Получение списка файлов
response = requests.get('http://localhost:8000/data/list-files')
files = response.json()['files']
print(f"Total files: {len(files)}")

# Получение информации о файле
filename = files[0]['filename']
response = requests.get(f'http://localhost:8000/data/file-info/{filename}')
info = response.json()
print(f"Rows: {info['rows']}, Columns: {info['column_count']}")
```

### JavaScript (fetch)

```javascript
// Загрузка файла
const formData = new FormData();
const fileInput = document.querySelector('input[type="file"]');
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/data/upload-csv', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log('Uploaded:', data))
  .catch(error => console.error('Error:', error));

// Получение списка файлов
fetch('http://localhost:8000/data/list-files')
  .then(response => response.json())
  .then(data => {
    console.log('Files:', data.files);
    console.log('Total:', data.total_count);
  });
```

### Postman

1. **Загрузка файла:**
   - Method: POST
   - URL: `http://localhost:8000/data/upload-csv`
   - Body: form-data
   - Key: `file` (type: File)
   - Value: Select your CSV file

2. **Список файлов:**
   - Method: GET
   - URL: `http://localhost:8000/data/list-files`

3. **Информация о файле:**
   - Method: GET
   - URL: `http://localhost:8000/data/file-info/your_filename.csv`

4. **Удаление файла:**
   - Method: DELETE
   - URL: `http://localhost:8000/data/delete-file/your_filename.csv`

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос (GET) |
| 201 | Файл успешно загружен (POST) |
| 400 | Неверный формат файла или имя файла |
| 404 | Файл не найден |
| 500 | Внутренняя ошибка сервера |

---

## Безопасность

- Принимаются только файлы с расширением `.csv`
- Имена файлов автоматически санитизируются
- Защита от path traversal атак
- Файлы сохраняются только в `data/processed`
- Автоматическое добавление timestamp к именам файлов предотвращает перезапись существующих файлов

---

## Интеграция с существующими системами

После загрузки CSV файлов через этот API, они автоматически доступны для:
- Анализа через `/query` эндпоинт с AI агентом
- Использования в аналитических эндпоинтах `/analytics/*`
- Обработки скриптами в `scripts/` директории

Загруженные файлы сразу же становятся частью общего датасета и могут быть использованы для генерации отчетов и аналитики.

