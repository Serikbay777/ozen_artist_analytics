"""
Test script for new tool-based agent
"""

import requests
import json
import time

API_URL = "http://localhost:8002/query"
TEST_UUID = "b5222ce6-03c5-4959-ac9e-a3898ebfe075"

# Тестовые вопросы
TEST_QUESTIONS = [
    "Какие платформы самые популярные?",
    "Топ 10 артистов по выручке",
    "Какой доход по странам?",
    "Покажи рост артистов за последние годы",
    "Какие треки самые прибыльные?",
    "Сколько всего денег заработали?",
    "Какие артисты растут быстрее всего?",
    "Покажи статистику по Spotify",
]


def test_question(question: str):
    """Test a single question"""
    print("\n" + "="*80)
    print(f"📝 Вопрос: {question}")
    print("="*80)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "uuid": TEST_UUID
            },
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успех! (время: {elapsed_time:.2f}s)")
            print(f"\n🔧 Использованный инструмент: {data.get('tool_used', 'N/A')}")
            print(f"📊 Параметры: {data.get('tool_parameters', {})}")
            print(f"\n💬 Ответ:\n{data.get('answer', 'N/A')}")
        else:
            print(f"❌ Ошибка {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Таймаут (>30 секунд)")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")


def main():
    print("🚀 Тестирование Tool-Based Agent")
    print("="*80)
    print(f"API: {API_URL}")
    print(f"UUID: {TEST_UUID}")
    print(f"Вопросов: {len(TEST_QUESTIONS)}")
    
    # Проверяем доступность API
    try:
        response = requests.get("http://localhost:8002/docs")
        if response.status_code != 200:
            print("\n⚠️ API не доступен. Запусти сервер:")
            print("   python -m uvicorn app.main:app --reload --port 8002")
            return
    except:
        print("\n⚠️ API не доступен. Запусти сервер:")
        print("   python -m uvicorn app.main:app --reload --port 8002")
        return
    
    print("\n✅ API доступен, начинаем тесты...\n")
    
    # Тестируем каждый вопрос
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}]")
        test_question(question)
        time.sleep(1)  # Небольшая пауза между запросами
    
    print("\n" + "="*80)
    print("✅ Тестирование завершено!")
    print("="*80)


if __name__ == "__main__":
    main()

