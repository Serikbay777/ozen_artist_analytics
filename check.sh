#!/bin/bash
# Полная проверка Docker развертывания

echo "🔍 Проверка Music Analyzer Agent"
echo "================================="
echo ""

# 1. Проверка что Docker запущен
echo "1️⃣ Проверка Docker..."
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker работает"
else
    echo "   ❌ Docker не запущен"
    exit 1
fi

# 2. Проверка .env файла
echo ""
echo "2️⃣ Проверка .env файла..."
if [ -f .env ]; then
    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo "   ✅ .env файл существует с ANTHROPIC_API_KEY"
    else
        echo "   ⚠️  .env есть, но нет ANTHROPIC_API_KEY"
    fi
else
    echo "   ❌ .env файл не найден"
    echo "   Создайте: cp .env.example .env"
    exit 1
fi

# 3. Проверка что контейнер запущен
echo ""
echo "3️⃣ Проверка контейнера..."
if docker-compose ps | grep -q "Up"; then
    echo "   ✅ Контейнер запущен"
    
    # 4. Проверка структуры внутри контейнера
    echo ""
    echo "4️⃣ Проверка структуры в контейнере..."
    docker-compose exec -T api ls -la /app/ > /dev/null 2>&1 && echo "   ✅ /app/ существует"
    docker-compose exec -T api ls /app/app/api.py > /dev/null 2>&1 && echo "   ✅ app/api.py на месте"
    docker-compose exec -T api ls /app/data/ > /dev/null 2>&1 && echo "   ✅ data/ примонтирована"
    docker-compose exec -T api ls /app/schema_only.db > /dev/null 2>&1 && echo "   ✅ база данных на месте"
    
    # 5. Проверка переменных окружения
    echo ""
    echo "5️⃣ Проверка env переменных в контейнере..."
    if docker-compose exec -T api env | grep -q "ANTHROPIC_API_KEY"; then
        echo "   ✅ ANTHROPIC_API_KEY передан в контейнер"
    else
        echo "   ❌ ANTHROPIC_API_KEY не найден в контейнере"
    fi
    
else
    echo "   ⚠️  Контейнер не запущен"
    echo "   Запустите: docker-compose up -d"
    exit 1
fi

# 6. Проверка API
echo ""
echo "6️⃣ Проверка доступности API..."
sleep 2  # Подождем пару секунд
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "   ✅ API доступен на http://localhost:8000"
else
    echo "   ❌ API не отвечает"
    echo "   Проверьте логи: docker-compose logs"
    exit 1
fi

# 7. Тестовый запрос к /query
echo ""
echo "7️⃣ Тестовый запрос к AI агенту..."
echo "   Отправляем: 'Покажи топ 3 артистов'"
response=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Покажи топ 3 артистов по доходу"}' \
  --max-time 30)

if [ -n "$response" ]; then
    echo "   ✅ AI агент ответил"
    echo ""
    echo "   Ответ:"
    echo "   --------------------------------"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo "   --------------------------------"
else
    echo "   ❌ Нет ответа от агента"
fi

echo ""
echo "================================="
echo "✅ Проверка завершена!"
echo ""
echo "📖 Документация: http://localhost:8000/docs"
echo "🔍 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"

