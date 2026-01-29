from langgraph.graph import StateGraph
from app.agents.State import State
from app.agents.ToolAgent import ToolAgent
from langgraph.graph import END
import logging

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Tool-based workflow manager для музыкальной аналитики.
    Упрощенный пайплайн: выбор инструмента → выполнение → форматирование
    """
    
    def __init__(self):
        self.tool_agent = ToolAgent()

    def create_workflow(self) -> StateGraph:
        """Создание упрощенного графа workflow с инструментами."""
        workflow = StateGraph(State)

        # Добавляем узлы для работы с инструментами
        workflow.add_node("select_tool", self.tool_agent.select_tool)
        workflow.add_node("execute_tool", self.tool_agent.execute_tool)
        workflow.add_node("format_results", self.tool_agent.format_results)
        
        # Упрощенный граф: select → execute → format
        workflow.add_edge("select_tool", "execute_tool")
        workflow.add_edge("execute_tool", "format_results")
        workflow.add_edge("format_results", END)
        
        # Точка входа - выбор инструмента
        workflow.set_entry_point("select_tool")

        return workflow
    
    def returnGraph(self):
        """Возвращает скомпилированный граф."""
        return self.create_workflow().compile()

    def run_tool_agent(self, question: str, uuid: str, artist_name: str = None) -> dict:
        """Запуск tool-based workflow."""
        logger.info(">>> Запуск tool-based workflow")
        app = self.create_workflow().compile()
        
        logger.info(f">>> Вопрос: {question}")
        logger.info(f">>> Артист: {artist_name or 'Общая аналитика'}")
        result = app.invoke({
            "question": question, 
            "uuid": uuid,
            "artist_name": artist_name
        })
        
        logger.info(">>> Workflow завершен")
        logger.info(f"    - Инструмент: {result.get('tool_name', 'N/A')}")
        logger.info(f"    - Ответ: {bool(result.get('answer'))}")
        
        return {
            "answer": result.get('answer', 'Ответ не сгенерирован'),
            "tool_used": result.get('tool_name'),
            "tool_parameters": result.get('tool_parameters')
        }
