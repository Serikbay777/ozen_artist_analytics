#!/bin/bash
# Простой тест для проверки что API работает

echo "🧪 Тестируем Music Analyzer API..."
echo ""

# Проверяем что API запущен
echo "1️⃣ Проверка доступности API..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API доступен на http://localhost:8000"
else
    echo "❌ API не доступен. Запустите: docker-compose up"
    exit 1
fi

echo ""
echo "2️⃣ Тестовый запрос к /query..."
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Покажи топ 5 артистов по доходу"}'

echo ""
echo ""
echo "✅ Тест завершен!"
echo "📖 Документация: http://localhost:8000/docs"
