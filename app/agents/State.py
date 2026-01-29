from typing import List, Any, Annotated, Dict, Optional
from typing_extensions import TypedDict
import operator

class State(TypedDict, total=False):
    # Input fields
    question: str
    uuid: str
    artist_name: Optional[str]  # Имя артиста для персонализации
    
    # Tool selection fields
    tool_name: str
    tool_parameters: Dict[str, Any]
    tool_reasoning: str
    is_relevant: bool
    
    # Processing fields (legacy, kept for compatibility)
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    sql_query: str
    sql_valid: bool
    sql_issues: str
    results: Any  # Can be dict or list
    
    # Output fields
    answer: str
    error: str
    visualization: str
    visualization_reason: str
    formatted_data_for_visualization: Dict[str, Any]

# Aliases for backward compatibility
InputState = State
OutputState = State