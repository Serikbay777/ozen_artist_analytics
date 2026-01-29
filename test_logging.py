"""
Простой скрипт для тестирования логирования
"""
import requests
import json

# URL вашего API
API_URL = "http://localhost:8000/query"

# Тестовый запрос
test_request = {
    "question": "What are the top 5 products by sales?",
    "uuid": "test-uuid-123"
}

print("Отправка тестового запроса...")
print(f"Вопрос: {test_request['question']}")
print(f"UUID: {test_request['uuid']}")
print("\n" + "="*50)
print("Проверьте логи сервера для отслеживания процесса")
print("="*50 + "\n")

try:
    response = requests.post(API_URL, json=test_request)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Запрос успешно обработан!")
        print(f"\nОтвет: {result.get('answer', 'N/A')}")
        print(f"Визуализация: {result.get('visualization', 'N/A')}")
        print(f"Причина визуализации: {result.get('visualization_reason', 'N/A')}")
    else:
        print(f"✗ Ошибка: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("✗ Не удалось подключиться к серверу")
    print("Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
except Exception as e:
    print(f"✗ Ошибка: {str(e)}")

