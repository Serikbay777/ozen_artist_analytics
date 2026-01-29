"""
Test script for artist personalized chat
"""

import requests
import json

API_URL = "http://localhost:8002/query"
TEST_UUID = "test"

# Тестовые вопросы от артиста
TEST_SCENARIOS = [
    {
        "artist": "Darkhan Juzz",
        "questions": [
            "Сколько у меня стримов?",
            "Какая моя общая выручка?",
            "Покажи мои топ треки",
            "На каких платформах меня больше слушают?",
            "В каких странах я популярен?",
        ]
    },
    {
        "artist": None,  # Общая аналитика
        "questions": [
            "Какие платформы самые популярные?",
            "Топ 10 артистов по выручке",
        ]
    }
]


def test_question(question: str, artist_name: str = None):
    """Test a single question"""
    print("\n" + "="*80)
    if artist_name:
        print(f"🎤 Артист: {artist_name}")
    print(f"📝 Вопрос: {question}")
    print("="*80)
    
    try:
        payload = {
            "question": question,
            "uuid": TEST_UUID
        }
        
        if artist_name:
            payload["artist_name"] = artist_name
        
        response = requests.post(
            API_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успех!")
            print(f"\n🔧 Инструмент: {data.get('tool_used', 'N/A')}")
            print(f"\n💬 Ответ:\n{data.get('answer', 'N/A')}")
        else:
            print(f"❌ Ошибка {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Таймаут (>30 секунд)")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")


def main():
    print("🚀 Тестирование персонализированного чата с артистом")
    print("="*80)
    print(f"API: {API_URL}")
    
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
    
    # Тестируем сценарии
    for scenario in TEST_SCENARIOS:
        artist = scenario["artist"]
        questions = scenario["questions"]
        
        if artist:
            print(f"\n{'='*80}")
            print(f"🎤 СЦЕНАРИЙ: Чат с артистом {artist}")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print(f"📊 СЦЕНАРИЙ: Общая аналитика")
            print(f"{'='*80}")
        
        for question in questions:
            test_question(question, artist)
            print()
    
    print("\n" + "="*80)
    print("✅ Тестирование завершено!")
    print("="*80)
    
    print("\n💡 Примеры запросов для Telegram бота:")
    print("""
    # Запрос от артиста
    {
        "question": "Сколько у меня стримов?",
        "artist_name": "Darkhan Juzz",
        "uuid": "telegram_user_id"
    }
    
    # Общий запрос (без артиста)
    {
        "question": "Какие платформы самые популярные?",
        "uuid": "telegram_user_id"
    }
    """)


if __name__ == "__main__":
    main()

