"""
Tool-based Agent for analytics
Selects and executes appropriate analytics tools based on user questions
"""

from langchain_core.prompts import ChatPromptTemplate
from app.agents.LLMManager import LLMManager
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
        logger.info(f"✅ Инициализирован ToolAgent")
    
    def select_tool(self, state: dict) -> dict:
        """
        Step 1: Select appropriate tool and parameters based on question
        """
        logger.info("→ Выбор инструмента")
        question = state['question']
        artist_name = state.get('artist_name')
        
        # TODO: Implement tool selection logic
        
        return {
            "tool_name": "placeholder",
            "tool_parameters": {},
            "tool_reasoning": "placeholder",
            "is_relevant": True
        }
    
    def execute_tool(self, state: dict) -> dict:
        """
        Step 2: Execute selected tool with parameters
        """
        logger.info("→ Выполнение инструмента")
        
        # TODO: Implement tool execution logic
        
        return {"results": {}}
    
    def format_results(self, state: dict) -> dict:
        """
        Step 3: Format tool results into human-readable answer
        """
        logger.info("→ Форматирование результатов")
        question = state['question']
        results = state.get('results')
        
        # TODO: Implement result formatting logic
        
        return {"answer": "Placeholder answer"}

