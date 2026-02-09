from typing import List, Any, Annotated, Dict, Optional
from typing_extensions import TypedDict
import operator

class State(TypedDict, total=False):
    # Input fields
    question: str
    uuid: str
    artist_name: Optional[str]  # Имя артиста для персонализации
    
    # Orchestrator fields
    selected_agent: str  # Какой агент выбран оркестратором
    routing_reasoning: str  # Почему выбран этот агент
    routing_confidence: str  # Уверенность в выборе (high/medium/low)
    
    # Agent execution fields
    agent_used: str  # Какой агент фактически обработал запрос
    
    # Tool selection fields (для Analytics Agent)
    tool_name: str
    tool_parameters: Dict[str, Any]
    tool_reasoning: str
    tool_used: str  # Какой инструмент был использован
    is_relevant: bool
    
    # Processing fields
    results: Any  # Результаты выполнения инструмента или запроса
    
    # Output fields
    answer: str
    error: str
    
    # Legacy fields (kept for backward compatibility)
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    sql_query: str
    sql_valid: bool
    sql_issues: str
    visualization: str
    visualization_reason: str
    formatted_data_for_visualization: Dict[str, Any]

# Aliases for backward compatibility
InputState = State
OutputState = State