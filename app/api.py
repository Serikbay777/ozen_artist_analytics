from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from app.agents.WorkflowManager import WorkflowManager
from app.routers import analytics, artist_analytics, data_management, reports
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Music Analyzer Agent API",
    description="API for music analytics and AI-powered queries",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router)
app.include_router(artist_analytics.router)
app.include_router(data_management.router)
app.include_router(reports.router)

# Initialize agent
workflow_manager = WorkflowManager()


class QueryRequest(BaseModel):
    question: str
    uuid: Optional[str] = None
    artist_name: Optional[str] = None  # Имя артиста для персонализации


@app.post("/query")
async def query(request: QueryRequest):
    """Run agent on question"""
    logger.info("=" * 80)
    logger.info("=== ПОЛУЧЕН НОВЫЙ ЗАПРОС /query ===")
    logger.info(f"Вопрос: {request.question}")
    logger.info(f"UUID: {request.uuid}")
    logger.info(f"Артист: {request.artist_name or 'Не указан'}")
    logger.info("=" * 80)
    
    try:
        result = workflow_manager.run_tool_agent(
            question=request.question,
            uuid=request.uuid,
            artist_name=request.artist_name
        )
        logger.info("=" * 80)
        logger.info("=== ЗАПРОС УСПЕШНО ОБРАБОТАН ===")
        logger.info(f"Инструмент: {result.get('tool_used', 'N/A')}")
        logger.info(f"Ответ: {result.get('answer', 'N/A')[:200]}...")
        logger.info("=" * 80)
        return result
    except Exception as e:
        logger.error("=" * 80)
        logger.error("=== ОШИБКА ПРИ ОБРАБОТКЕ ЗАПРОСА ===")
        logger.error(f"Ошибка: {str(e)}", exc_info=True)
        logger.error("=" * 80)
        raise
