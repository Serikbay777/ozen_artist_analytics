"""
Быстрый тест системы
"""

from dotenv import load_dotenv
from app.agents.WorkflowManager import WorkflowManager

# Загрузка переменных окружения
load_dotenv()

def quick_test():
    print("\n" + "=" * 60)
    print("БЫСТРЫЙ ТЕСТ FAQ АГЕНТОВ")
    print("=" * 60 + "\n")
    
    workflow_manager = WorkflowManager()
    
    # Тестовые вопросы для разных агентов
    test_questions = [
        "Как верифицироваться в Spotify?",
        "Какой размер обложки для Apple Music?",
        "Как создать караоке для Apple Music?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"ТЕСТ {i}/{len(test_questions)}")
        print(f"{'=' * 60}")
        print(f"Вопрос: {question}\n")
        print("Обработка...")
        
        result = workflow_manager.run_agent_workflow(
            question=question,
            uuid=f"quick-test-{i}"
        )
        
        print("\n" + "-" * 60)
        print("РЕЗУЛЬТАТ:")
        print("-" * 60)
        print(f"Агент: {result.get('agent_used')}")
        print(f"Уверенность: {result.get('routing_confidence')}")
        print(f"\nОтвет:\n{result.get('answer')[:300]}...")
        print("\n")
    
    print("=" * 60)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    quick_test()
