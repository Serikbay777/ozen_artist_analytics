"""
Artist Report Generation Tools
Generates professional PDF reports for artists
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService
import os
import logging

logger = logging.getLogger(__name__)


class GenerateArtistReportTool(BaseTool):
    """Generate a professional PDF quarterly report for an artist"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "generate_artist_report"
    
    @property
    def description(self) -> str:
        return """Создать профессиональный PDF-отчет для артиста. 
        Используй этот инструмент когда пользователь просит:
        - 'Сделай отчет для артиста X'
        - 'Создай PDF-отчет для X'
        - 'Квартальный отчет для артиста X'
        - 'Сформируй отчет по артисту X'
        Отчет включает: KPI, топ-треки, платформы, географию, динамику, графики и рекомендации."""
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Имя артиста (точное или частичное совпадение)",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период отчета (например: 'Q4 2025', '2025')",
                required=False,
                default="Q4 2025"
            ),
            ToolParameter(
                name="include_medialand",
                type="boolean",
                description="Включить данные Medialand (авторские отчисления)",
                required=False,
                default=False
            )
        ]
    
    def execute(self, artist_name: str, period: str = "Q4 2025", include_medialand: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute PDF report generation for artist"""
        
        logger.info(f"🎯 Генерация отчета для артиста: {artist_name}")
        logger.info(f"   Период: {period}")
        logger.info(f"   Medialand: {'да' if include_medialand else 'нет'}")
        
        try:
            # Импортируем генератор отчетов
            from app.utils.artist_report_generator import ArtistReportGenerator
            
            # Создаем генератор
            generator = ArtistReportGenerator(self.analytics)
            
            # Генерируем отчет
            result = generator.generate_report(
                artist_name=artist_name,
                period=period,
                include_medialand=include_medialand
            )
            
            if result['success']:
                logger.info(f"✅ Отчет успешно создан: {result['pdf_path']}")
                
                # Добавляем информацию для скачивания
                pdf_filename = os.path.basename(result['pdf_path'])
                download_url = f"/reports/download/{pdf_filename}"
                
                return {
                    "success": True,
                    "artist_name": result['artist_name'],
                    "pdf_path": result['pdf_path'],
                    "pdf_filename": pdf_filename,
                    "download_url": download_url,
                    "summary": result['summary'],
                    "message": f"✅ **PDF-отчет успешно создан для артиста {result['artist_name']}**\n\n"
                              f"📥 **Скачать отчет:** [Скачать PDF]({download_url})\n"
                              f"📄 **Файл:** `{pdf_filename}`\n\n"
                              f"{result['summary']}"
                }
            else:
                logger.error(f"❌ Ошибка генерации: {result['error']}")
                return {
                    "success": False,
                    "error": result['error'],
                    "message": f"❌ Не удалось создать отчет: {result['error']}"
                }
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Критическая ошибка при создании отчета: {str(e)}"
            }

