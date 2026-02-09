from langgraph.graph import StateGraph
from app.agents.State import State
from app.agents.OrchestratorAgent import OrchestratorAgent
from app.agents.faq import VerificationAgent, ReleaseCoverAgent, LyricsAgent
from langgraph.graph import END
import logging

logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    Multi-agent workflow manager с оркестратором
    Архитектура: Orchestrator → FAQ Agents (Verification/ReleaseCover/Lyrics)
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.verification_agent = VerificationAgent()
        self.release_cover_agent = ReleaseCoverAgent()
        self.lyrics_agent = LyricsAgent()
        logger.info("✅ WorkflowManager инициализирован с 3 FAQ агентами")

    def create_workflow(self) -> StateGraph:
        """Создание графа workflow с оркестратором и FAQ агентами"""
        workflow = StateGraph(State)

        # Добавляем узлы
        workflow.add_node("orchestrator", self.orchestrator.route_question)
        workflow.add_node("verification_agent", self.verification_agent.answer)
        workflow.add_node("release_cover_agent", self.release_cover_agent.answer)
        workflow.add_node("lyrics_agent", self.lyrics_agent.answer)
        
        # Функция роутинга после оркестратора
        def route_to_agent(state: dict) -> str:
            """Роутинг к нужному агенту"""
            selected_agent = state.get('selected_agent', 'verification_agent')
            logger.info(f"  → Роутинг к: {selected_agent}")
            return selected_agent
        
        # Точка входа - оркестратор
        workflow.set_entry_point("orchestrator")
        
        # Условный роутинг от оркестратора к агентам
        workflow.add_conditional_edges(
            "orchestrator",
            route_to_agent,
            {
                "verification_agent": "verification_agent",
                "release_cover_agent": "release_cover_agent",
                "lyrics_agent": "lyrics_agent"
            }
        )
        
        # Все агенты ведут к END
        workflow.add_edge("verification_agent", END)
        workflow.add_edge("release_cover_agent", END)
        workflow.add_edge("lyrics_agent", END)

        return workflow
    
    def returnGraph(self):
        """Возвращает скомпилированный граф"""
        return self.create_workflow().compile()

    def run_agent_workflow(self, question: str, uuid: str, artist_name: str = None) -> dict:
        """Запуск multi-agent workflow"""
        logger.info("=" * 80)
        logger.info(">>> Запуск Multi-Agent Workflow")
        logger.info("=" * 80)
        
        app = self.create_workflow().compile()
        
        logger.info(f">>> Вопрос: {question}")
        logger.info(f">>> Артист: {artist_name or 'Общий вопрос'}")
        logger.info(f">>> UUID: {uuid}")
        
        result = app.invoke({
            "question": question, 
            "uuid": uuid,
            "artist_name": artist_name
        })
        
        logger.info("=" * 80)
        logger.info(">>> Workflow завершен")
        logger.info(f"    - Выбранный агент: {result.get('selected_agent', 'N/A')}")
        logger.info(f"    - Использованный агент: {result.get('agent_used', 'N/A')}")
        logger.info(f"    - Уверенность: {result.get('routing_confidence', 'N/A')}")
        logger.info("=" * 80)
        
        return {
            "answer": result.get('answer', 'Ответ не сгенерирован'),
            "agent_used": result.get('agent_used'),
            "routing_confidence": result.get('routing_confidence')
        }
    
    # Backward compatibility
    def run_tool_agent(self, question: str, uuid: str, artist_name: str = None) -> dict:
        """Обратная совместимость - перенаправляет на новый метод"""
        logger.warning("⚠️  run_tool_agent deprecated, используйте run_agent_workflow")
        return self.run_agent_workflow(question, uuid, artist_name)
