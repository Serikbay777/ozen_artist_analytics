"""
Тестовый скрипт для проверки работы multi-agent системы
"""

from dotenv import load_dotenv
from app.agents.WorkflowManager import WorkflowManager
import logging

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_agents():
    """Тестирование различных типов вопросов"""
    
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ MULTI-AGENT СИСТЕМЫ")
    print("=" * 80 + "\n")
    
    # Инициализация
    workflow_manager = WorkflowManager()
    
    # Тестовые вопросы
    test_cases = [
        {
            "question": "Как верифицироваться в Spotify?",
            "artist_name": None,
            "expected_agent": "verification",
            "description": "Верификация в Spotify"
        },
        {
            "question": "Какие документы нужны для Apple Music?",
            "artist_name": None,
            "expected_agent": "verification",
            "description": "Документы для Apple Music"
        },
        {
            "question": "Сколько времени занимает верификация в VK Studio?",
            "artist_name": "Test Artist",
            "expected_agent": "verification",
            "description": "Время верификации VK"
        },
        {
            "question": "Как зарегистрироваться в BandLink для Яндекс Музыки?",
            "artist_name": None,
            "expected_agent": "verification",
            "description": "Регистрация в BandLink"
        },
        {
            "question": "Что нужно для подтверждения профиля артиста?",
            "artist_name": None,
            "expected_agent": "verification",
            "description": "Подтверждение профиля"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"ТЕСТ {i}/{len(test_cases)}: {test_case['description']}")
        print(f"{'=' * 80}")
        print(f"Вопрос: {test_case['question']}")
        print(f"Артист: {test_case['artist_name'] or 'Не указан'}")
        print(f"Ожидаемый агент: {test_case['expected_agent']}")
        print(f"{'-' * 80}")
        
        try:
            result = workflow_manager.run_agent_workflow(
                question=test_case['question'],
                uuid=f"test-{i}",
                artist_name=test_case['artist_name']
            )
            
            agent_used = result.get('agent_used', 'N/A')
            success = agent_used == test_case['expected_agent']
            
            print(f"\n✓ РЕЗУЛЬТАТ:")
            print(f"  - Использованный агент: {agent_used}")
            print(f"  - Уверенность: {result.get('routing_confidence', 'N/A')}")
            print(f"  - Соответствие ожиданиям: {'✅ ДА' if success else '❌ НЕТ'}")
            print(f"\n  ОТВЕТ:")
            print(f"  {result.get('answer', 'Нет ответа')[:400]}...")
            
            results.append({
                "test": test_case['description'],
                "success": success,
                "agent_used": agent_used,
                "expected": test_case['expected_agent']
            })
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {str(e)}")
            results.append({
                "test": test_case['description'],
                "success": False,
                "error": str(e)
            })
    
    # Итоги
    print(f"\n\n{'=' * 80}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print(f"{'=' * 80}")
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"\nУспешных тестов: {successful}/{total}")
    print(f"Процент успеха: {successful/total*100:.1f}%\n")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.get('success', False) else "❌"
        print(f"{status} Тест {i}: {result['test']}")
        if 'agent_used' in result:
            print(f"   Агент: {result['agent_used']} (ожидался: {result.get('expected', 'N/A')})")
        if 'error' in result:
            print(f"   Ошибка: {result['error']}")
    
    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    test_agents()
