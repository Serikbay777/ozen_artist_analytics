# Multi-Agent Architecture

## 🏗️ Архитектура

Система построена на базе **LangGraph** с паттерном **Orchestrator + Specialized Agents**.

```
┌─────────────────────────────────────────────────────────────┐
│                      USER QUESTION                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                         │
│  Анализирует вопрос и выбирает подходящего агента          │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ VERIFICATION │ │  ANALYTICS   │ │   GENERAL    │
│    AGENT     │ │    AGENT     │ │    AGENT     │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ FAQ вопросы  │ │ Статистика   │ │ Общие        │
│ о верифика-  │ │ и аналитика  │ │ вопросы      │
│ ции          │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FORMATTED ANSWER                         │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Компоненты

### 1. **OrchestratorAgent** (`app/agents/OrchestratorAgent.py`)

**Роль:** Главный роутер, определяет тип вопроса и выбирает агента

**Логика выбора:**
- `verification_agent` - вопросы о верификации на платформах
- `analytics_agent` - вопросы о статистике, доходе, стримах
- `general_agent` - все остальные вопросы

**Выход:**
```python
{
    "selected_agent": "verification_agent",
    "routing_reasoning": "Вопрос про верификацию на конкретной платформе",
    "routing_confidence": "high"  # high/medium/low
}
```

### 2. **VerificationAgent** (`app/agents/faq/VerificationAgent.py`)

**Роль:** Отвечает на вопросы о верификации артистов

**База знаний:** `app/services/faq/verification.txt`

**Покрывает:**
- Apple Music for Artists
- Spotify for Artists
- BandLink x Яндекс Музыка
- VK Studio

**Примеры вопросов:**
- "Как верифицироваться в Spotify?"
- "Какие документы нужны для Apple Music?"
- "Сколько времени занимает верификация?"

### 3. **AnalyticsAgent** (`app/agents/AnalyticsAgent.py`)

**Роль:** Обрабатывает аналитические вопросы

**Pipeline:**
1. **Tool Selection** - выбирает подходящий инструмент аналитики
2. **Tool Execution** - выполняет инструмент с параметрами
3. **Result Formatting** - форматирует результаты в читаемый ответ

**Доступные инструменты:**
- `get_artist_streams` - статистика стримов артиста
- `get_artist_platforms` - статистика по платформам
- `get_artist_geography` - географическая статистика
- `get_artist_tracks` - статистика по трекам
- `get_artist_full_analytics` - полная аналитика
- `search_artists` - поиск артистов

**Примеры вопросов:**
- "Сколько я заработал?"
- "Топ 10 артистов по выручке"
- "Какие платформы самые популярные?"

### 4. **GeneralAgent** (`app/agents/GeneralAgent.py`)

**Роль:** Обрабатывает общие вопросы

**Примеры вопросов:**
- "Привет, как дела?"
- "Что такое õzen?"
- "Как с вами связаться?"

## 🔄 Workflow

### LangGraph граф:

```python
orchestrator → [conditional routing] → {
    verification_agent → END
    analytics_agent → END
    general_agent → END
}
```

### Пример выполнения:

```python
# 1. Вопрос поступает
question = "Как верифицироваться в Spotify?"

# 2. Orchestrator анализирует
orchestrator.route_question(state) 
# → selected_agent: "verification_agent"

# 3. Conditional routing направляет к агенту
route_to_agent(state)
# → "verification_agent"

# 4. VerificationAgent обрабатывает
verification_agent.answer(state)
# → answer: "🎵 **Верификация в Spotify for Artists**..."

# 5. Результат возвращается пользователю
```

## 📁 Структура файлов

```
app/
├── agents/
│   ├── OrchestratorAgent.py      # Главный роутер
│   ├── AnalyticsAgent.py          # Аналитический агент
│   ├── GeneralAgent.py            # Общий агент
│   ├── WorkflowManager.py         # Управление LangGraph workflow
│   ├── State.py                   # Определение состояния
│   ├── LLMManager.py              # Управление LLM
│   └── faq/
│       ├── __init__.py
│       └── VerificationAgent.py   # FAQ агент для верификации
│
├── services/
│   └── faq/
│       └── verification.txt       # База знаний о верификации
│
└── tools/
    └── artist_analytics_agent_tools.py  # Инструменты аналитики
```

## 🚀 Использование

### Через API:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Как верифицироваться в Spotify?",
    "artist_name": "Artist Name"
  }'
```

### Через Python:

```python
from app.agents.WorkflowManager import WorkflowManager

workflow_manager = WorkflowManager()

result = workflow_manager.run_agent_workflow(
    question="Как верифицироваться в Spotify?",
    uuid="unique-id",
    artist_name="Artist Name"  # опционально
)

print(result['answer'])
print(f"Агент: {result['agent_used']}")
print(f"Уверенность: {result['routing_confidence']}")
```

### Тестирование:

```bash
python test_agents.py
```

## 🔧 Добавление нового FAQ агента

### Шаг 1: Создайте файл базы знаний

```bash
# app/services/faq/new_topic.txt
Содержимое базы знаний...
```

### Шаг 2: Создайте агента

```python
# app/agents/faq/NewTopicAgent.py

from langchain_core.prompts import ChatPromptTemplate
from app.agents.LLMManager import LLMManager
import logging
import os

logger = logging.getLogger(__name__)

class NewTopicAgent:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.knowledge_base = self._load_knowledge_base()
        logger.info("✅ Инициализирован NewTopicAgent")
    
    def _load_knowledge_base(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        faq_path = os.path.join(base_dir, 'services', 'faq', 'new_topic.txt')
        
        with open(faq_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def answer(self, state: dict) -> dict:
        question = state['question']
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Ты эксперт по [тема].

БАЗА ЗНАНИЙ:
{knowledge_base}

ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе информации из базы знаний
2. Форматируй ответ в markdown
3. Используй эмодзи для наглядности
"""),
            ("human", "{question}"),
        ])
        
        response = self.llm_manager.invoke(
            prompt,
            question=question,
            knowledge_base=self.knowledge_base
        )
        
        return {
            "answer": response,
            "agent_used": "new_topic"
        }
```

### Шаг 3: Обновите Orchestrator

```python
# В OrchestratorAgent.py добавьте в список агентов:

3. **new_topic_agent** - Вопросы о [тема]
   - Примеры вопросов...
```

### Шаг 4: Обновите WorkflowManager

```python
# В WorkflowManager.py:

from app.agents.faq import VerificationAgent, NewTopicAgent

def __init__(self):
    # ...
    self.new_topic_agent = NewTopicAgent()

def create_workflow(self):
    # ...
    workflow.add_node("new_topic_agent", self.new_topic_agent.answer)
    
    workflow.add_conditional_edges(
        "orchestrator",
        route_to_agent,
        {
            # ...
            "new_topic_agent": "new_topic_agent"
        }
    )
    
    workflow.add_edge("new_topic_agent", END)
```

## 📊 State Schema

```python
State = {
    # Input
    "question": str,
    "uuid": str,
    "artist_name": Optional[str],
    
    # Orchestrator
    "selected_agent": str,
    "routing_reasoning": str,
    "routing_confidence": str,
    
    # Agent execution
    "agent_used": str,
    
    # Analytics Agent specific
    "tool_name": str,
    "tool_parameters": dict,
    "tool_used": str,
    "results": Any,
    
    # Output
    "answer": str,
    "error": str
}
```

## 🎯 Преимущества архитектуры

1. **Модульность** - каждый агент независим и отвечает за свою область
2. **Масштабируемость** - легко добавлять новых агентов
3. **Прозрачность** - видно какой агент обработал запрос
4. **Специализация** - каждый агент оптимизирован для своей задачи
5. **Maintainability** - легко обновлять базы знаний и логику

## 🔍 Логирование

Каждый шаг workflow логируется:

```
>>> Запуск Multi-Agent Workflow
>>> Вопрос: Как верифицироваться в Spotify?
→ Orchestrator анализирует вопрос
  ✓ Выбран агент: verification_agent
  → Роутинг к: verification_agent
→ VerificationAgent обрабатывает вопрос
  ✓ Ответ сгенерирован (1234 символов)
>>> Workflow завершен
    - Выбранный агент: verification_agent
    - Использованный агент: verification
    - Уверенность: high
```

## 🐛 Отладка

Для детального логирования:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Для визуализации графа:

```python
workflow_manager = WorkflowManager()
graph = workflow_manager.returnGraph()
# Используйте LangGraph visualization tools
```
