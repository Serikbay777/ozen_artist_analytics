"""
Tool-based Agent for analytics
Selects and executes appropriate analytics tools based on user questions
"""

from langchain_core.prompts import ChatPromptTemplate
from app.agents.LLMManager import LLMManager
from app.tools import ALL_TOOLS
import logging
import json

logger = logging.getLogger(__name__)


class ToolAgent:
    """
    Agent that selects and executes analytics tools.
    Pipeline: question → tool selection → tool execution → format results
    """
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.tools = {tool.name: tool for tool in ALL_TOOLS}
        logger.info(f"✅ Инициализирован ToolAgent с {len(self.tools)} инструментами")
        for tool in ALL_TOOLS:
            logger.info(f"   - {tool.name}: {tool.description}")
    
    def select_tool(self, state: dict) -> dict:
        """
        Step 1: Select appropriate tool and parameters based on question
        """
        logger.info("→ Выбор инструмента")
        question = state['question']
        artist_name = state.get('artist_name')
        
        # Формируем описание всех доступных инструментов
        tools_description = "\n\n".join([
            f"**{tool.name}**\n"
            f"Описание: {tool.description}\n"
            f"Параметры: {json.dumps([p.dict() for p in tool.parameters], ensure_ascii=False, indent=2) if tool.parameters else 'Нет параметров'}"
            for tool in ALL_TOOLS
        ])
        
        # Добавляем контекст артиста если есть
        artist_context = ""
        if artist_name:
            artist_context = f"\n\n🎤 КОНТЕКСТ: Это чат с артистом **{artist_name}**. Вопросы относятся к его данным."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", '''Ты эксперт по музыкальной аналитике. Твоя задача - выбрать правильный инструмент для ответа на вопрос пользователя.{artist_context}

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:

{tools_description}

ВАЖНО:
1. Выбери ОДИН наиболее подходящий инструмент
2. Определи параметры для этого инструмента
3. Если вопрос не относится к аналитике, верни "NOT_RELEVANT"

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "tool_name": "название_инструмента",
  "parameters": {{
    "param1": value1,
    "param2": value2
  }},
  "reasoning": "почему выбран этот инструмент"
}}

Или если не релевантно:
{{
  "tool_name": "NOT_RELEVANT",
  "reasoning": "объяснение"
}}

ПРИМЕРЫ:

Вопрос: "Какие платформы самые популярные?"
Ответ:
{{
  "tool_name": "get_top_platforms",
  "parameters": {{"limit": 10}},
  "reasoning": "Вопрос про популярные платформы - нужна статистика платформ"
}}

Вопрос: "Топ 10 артистов по выручке"
Ответ:
{{
  "tool_name": "get_top_artists",
  "parameters": {{"limit": 10, "metric": "revenue"}},
  "reasoning": "Нужны топ артисты, отсортированные по выручке"
}}

Вопрос: "Какой рост у артистов?"
Ответ:
{{
  "tool_name": "get_artist_growth",
  "parameters": {{"limit": 20}},
  "reasoning": "Вопрос про рост артистов - нужна матрица роста"
}}

Вопрос: "Сколько всего денег заработали?"
Ответ:
{{
  "tool_name": "get_overview_stats",
  "parameters": {{}},
  "reasoning": "Общий вопрос про выручку - нужна общая статистика"
}}

Верни ТОЛЬКО JSON, без дополнительного текста.
'''),
            ("human", "Вопрос пользователя: {question}\n\nВыбери инструмент:"),
        ])
        
        response = self.llm_manager.invoke(
            prompt, 
            question=question,
            tools_description=tools_description,
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
            
            tool_selection = json.loads(response)
            tool_name = tool_selection.get("tool_name")
            parameters = tool_selection.get("parameters", {})
            reasoning = tool_selection.get("reasoning", "")
            
            logger.info(f"  ✓ Выбран инструмент: {tool_name}")
            logger.info(f"    Параметры: {parameters}")
            logger.info(f"    Обоснование: {reasoning}")
            
            if tool_name == "NOT_RELEVANT":
                return {
                    "tool_name": "NOT_RELEVANT",
                    "is_relevant": False
                }
            
            return {
                "tool_name": tool_name,
                "tool_parameters": parameters,
                "tool_reasoning": reasoning,
                "is_relevant": True
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ Ошибка парсинга JSON: {e}")
            logger.error(f"    Ответ LLM: {response}")
            return {
                "tool_name": "ERROR",
                "error": f"Не удалось распарсить ответ LLM: {str(e)}",
                "is_relevant": False
            }
    
    def execute_tool(self, state: dict) -> dict:
        """
        Step 2: Execute selected tool with parameters
        """
        logger.info("→ Выполнение инструмента")
        
        if not state.get('is_relevant', True):
            logger.info("  Запрос не релевантен, пропускаем выполнение")
            return {"results": "NOT_RELEVANT"}
        
        tool_name = state.get('tool_name')
        parameters = state.get('tool_parameters', {})
        artist_name = state.get('artist_name')
        
        # Добавляем artist_name в параметры если он есть
        if artist_name:
            parameters['artist_name'] = artist_name
            logger.info(f"  Фильтрация по артисту: {artist_name}")
        
        if tool_name not in self.tools:
            logger.error(f"  ✗ Инструмент {tool_name} не найден")
            return {
                "error": f"Инструмент {tool_name} не существует",
                "results": None
            }
        
        try:
            tool = self.tools[tool_name]
            logger.info(f"  Выполняем: {tool_name}({parameters})")
            
            results = tool.execute(**parameters)
            
            logger.info(f"  ✓ Инструмент выполнен успешно")
            logger.info(f"    Результат: {str(results)[:200]}...")
            
            return {"results": results}
            
        except Exception as e:
            logger.error(f"  ✗ Ошибка выполнения инструмента: {str(e)}")
            return {
                "error": str(e),
                "results": None
            }
    
    def format_results(self, state: dict) -> dict:
        """
        Step 3: Format tool results into human-readable answer
        """
        logger.info("→ Форматирование результатов")
        question = state['question']
        results = state.get('results')
        tool_name = state.get('tool_name')
        artist_name = state.get('artist_name')
        
        if results == "NOT_RELEVANT":
            logger.info("  Результаты не релевантны")
            return {
                "answer": "Извините, я могу отвечать только на вопросы о музыкальной аналитике из данных лейбла Озен."
            }
        
        if not results or 'error' in state:
            logger.info("  Нет результатов или ошибка")
            error_msg = state.get('error', 'Неизвестная ошибка')
            return {
                "answer": f"Не удалось получить результаты. Ошибка: {error_msg}"
            }
        
        # Персонализация для артиста
        personalization = ""
        if artist_name:
            personalization = f"\n\n🎤 ВАЖНО: Это ответ для артиста **{artist_name}**. Обращайся на \"ты\", используй \"у тебя\", \"твои треки\" и т.д."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", '''Ты аналитик музыкальных данных. Твоя задача - представить результаты инструмента аналитики в понятном виде.{personalization}

ПРАВИЛА:
1. Дай краткий, четкий ответ на вопрос пользователя
2. Используй данные из результатов инструмента
3. Форматируй ответ в markdown
4. Если данных много - покажи топ 5-10 с итогами
5. Добавь контекст и инсайты где уместно
6. Используй эмодзи для наглядности (📊 💰 🎵 🌍 и т.д.)

ПРИМЕРЫ:

Вопрос: "Какие платформы самые популярные?"
Результаты: {{"platforms": [{{"platform": "Spotify", "revenue": 450000, "streams": 180000000}}, ...]}}
Ответ:
"📊 **Самые популярные платформы по выручке:**

1. **Spotify** - €450,000 (180M стримов)
2. **YouTube Music** - €280,000 (120M стримов)
3. **Apple Music** - €180,000 (65M стримов)

💡 Spotify лидирует с большим отрывом, принося почти половину всей выручки."

Вопрос: "Топ 5 артистов"
Результаты: {{"artists": [{{"artist": "Darkhan Juzz", "revenue": 125000, "streams": 50000000}}, ...]}}
Ответ:
"🎤 **Топ 5 артистов по выручке:**

1. **Darkhan Juzz** - €125,000 (50M стримов)
2. **Artist 2** - €98,000 (42M стримов)
...

💰 Общая выручка топ-5: €450,000 (38% от всей выручки каталога)"
'''),
            ("human", '''Вопрос: {question}

Использованный инструмент: {tool_name}

Результаты: {results}

Сформулируй ответ:'''),
        ])
        
        response = self.llm_manager.invoke(
            prompt,
            question=question,
            tool_name=tool_name,
            results=json.dumps(results, ensure_ascii=False, indent=2),
            personalization=personalization
        )
        
        logger.info(f"  ✓ Ответ сформирован")
        logger.info(f"    Длина: {len(response)} символов")
        
        return {"answer": response}

