"""
Быстрый тест системы
"""

from dotenv import load_dotenv
from app.agents.WorkflowManager import WorkflowManager

# Загрузка переменных окружения
load_dotenv()

def quick_test():
    print("\n" + "=" * 60)
    print("БЫСТРЫЙ ТЕСТ VERIFICATION AGENT")
    print("=" * 60 + "\n")
    
    workflow_manager = WorkflowManager()
    
    question = "Как верифицироваться в Spotify?"
    
    print(f"Вопрос: {question}\n")
    print("Обработка...")
    
    result = workflow_manager.run_agent_workflow(
        question=question,
        uuid="quick-test"
    )
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ:")
    print("=" * 60)
    print(f"\nАгент: {result.get('agent_used')}")
    print(f"Уверенность: {result.get('routing_confidence')}")
    print(f"\nОтвет:\n{result.get('answer')}")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    quick_test()
