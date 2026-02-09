"""
Orchestrator Agent - главный агент-роутер
Определяет тип вопроса и направляет к соответствующему специализированному агенту
"""

from langchain_core.prompts import ChatPromptTemplate
from app.agents.LLMManager import LLMManager
import logging
import json

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Главный агент-оркестратор
    Анализирует вопрос и определяет, какой агент должен его обработать
    """
    
    def __init__(self):
        self.llm_manager = LLMManager()
        logger.info("✅ Инициализирован OrchestratorAgent")
    
    def route_question(self, state: dict) -> dict:
        """
        Определяет тип вопроса и выбирает подходящего агента
        """
        logger.info("→ Orchestrator анализирует вопрос")
        question = state['question']
        artist_name = state.get('artist_name')
        
        # Контекст артиста
        artist_context = ""
        if artist_name:
            artist_context = f"\n\n🎤 КОНТЕКСТ: Вопрос от артиста {artist_name}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Ты главный роутер вопросов для музыкального лейбла õzen.
Твоя задача - определить относится ли вопрос к верификации на платформах.{artist_context}

ДОСТУПНЫЙ АГЕНТ:

**verification_agent** - Вопросы о верификации на платформах
   - Как верифицироваться в Spotify/Apple Music/Яндекс/VK?
   - Какие документы нужны для верификации?
   - Сколько времени занимает верификация?
   - Как получить доступ к статистике на платформах?
   - Инструкции по регистрации и подтверждению профиля артиста

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "agent": "verification_agent",
  "reasoning": "почему выбран этот агент",
  "confidence": "high/medium/low"
}}

ПРИМЕРЫ:

Вопрос: "Как мне верифицироваться в Apple Music?"
Ответ:
{{
  "agent": "verification_agent",
  "reasoning": "Вопрос про верификацию на конкретной платформе",
  "confidence": "high"
}}

Вопрос: "Какие документы нужны для Spotify?"
Ответ:
{{
  "agent": "verification_agent",
  "reasoning": "Вопрос про документы для верификации",
  "confidence": "high"
}}

Вопрос: "Как зарегистрироваться в VK Studio?"
Ответ:
{{
  "agent": "verification_agent",
  "reasoning": "Вопрос про регистрацию и верификацию",
  "confidence": "high"
}}

Вопрос: "Сколько времени занимает проверка в Яндекс Музыке?"
Ответ:
{{
  "agent": "verification_agent",
  "reasoning": "Вопрос про процесс верификации",
  "confidence": "high"
}}

Верни ТОЛЬКО JSON, без дополнительного текста.
"""),
            ("human", "{question}"),
        ])
        
        response = self.llm_manager.invoke(
            prompt,
            question=question,
            artist_context=artist_context
        )
        
        # Парсим JSON ответ
        try:
            # Убираем markdown форматирование если есть
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            routing = json.loads(response)
            agent = routing.get("agent")
            reasoning = routing.get("reasoning", "")
            confidence = routing.get("confidence", "medium")
            
            logger.info(f"  ✓ Выбран агент: {agent}")
            logger.info(f"    Обоснование: {reasoning}")
            logger.info(f"    Уверенность: {confidence}")
            
            return {
                "selected_agent": agent,
                "routing_reasoning": reasoning,
                "routing_confidence": confidence
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ Ошибка парсинга JSON: {e}")
            logger.error(f"    Ответ LLM: {response}")
            # По умолчанию отправляем на general_agent
            return {
                "selected_agent": "general_agent",
                "routing_reasoning": "Ошибка роутинга, используем general agent",
                "routing_confidence": "low"
            }
