"""
Тестовый скрипт для проверки работы Qwen3 через Alem.ai API
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.LLMManager import LLMManager
from langchain_core.prompts import ChatPromptTemplate
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_qwen3():
    """Тестирование Qwen3 модели"""
    logger.info("=" * 80)
    logger.info("Тестирование Qwen3 через Alem.ai API")
    logger.info("=" * 80)
    
    try:
        # Инициализация LLM Manager
        llm_manager = LLMManager()
        
        # Простой тест
        logger.info("\n1️⃣ Простой тест: Hello, world!")
        prompt = ChatPromptTemplate.from_messages([
            ("user", "Hello, world! Ответь на русском языке.")
        ])
        
        response = llm_manager.invoke(prompt)
        logger.info(f"\n✅ Ответ получен:\n{response}\n")
        
        # Тест с системным промптом
        logger.info("\n2️⃣ Тест с системным промптом")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты эксперт по музыкальной индустрии. Отвечай кратко и по делу."),
            ("user", "Как верифицироваться в Spotify?")
        ])
        
        response = llm_manager.invoke(prompt)
        logger.info(f"\n✅ Ответ получен:\n{response}\n")
        
        # Тест JSON ответа (как в OrchestratorAgent)
        logger.info("\n3️⃣ Тест JSON ответа (роутинг)")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Определи тип вопроса и верни JSON:
{{
  "agent": "verification_agent | release_cover_agent | lyrics_agent",
  "reasoning": "почему выбран этот агент",
  "confidence": "high/medium/low"
}}

Верни ТОЛЬКО JSON, без дополнительного текста."""),
            ("user", "Какой размер обложки для Spotify?")
        ])
        
        response = llm_manager.invoke(prompt)
        logger.info(f"\n✅ Ответ получен:\n{response}\n")
        
        logger.info("=" * 80)
        logger.info("✅ Все тесты пройдены успешно!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_qwen3()
