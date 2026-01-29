# Как запустить

## 1. Подготовка

Создайте файл `.env` с вашим API ключом:

```bash
echo "ANTHROPIC_API_KEY=ваш_ключ" > .env
```

## 2. Запуск

### Docker (простой способ)

```bash
docker-compose up --build
```

### Локально (для разработки)

```bash
# Создать venv и установить зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запустить
python app/main.py
```

## 3. Проверка

Откройте в браузере:
- http://localhost:8000/docs (Docker)
- http://localhost:8002/docs (локально)

## 4. Тестовый запрос

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Покажи топ 5 артистов"}'
```

Готово! 🎉

