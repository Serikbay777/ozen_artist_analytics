"""
Country/Geography analytics tools
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService


class TopCountriesTool(BaseTool):
    """Get top countries by revenue or CPM"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_top_countries"
    
    @property
    def description(self) -> str:
        return "Получить топ стран по выручке или CPM. Показывает страну, выручку, стримы, CPM"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество стран (1-50)",
                required=False,
                default=15
            ),
            ToolParameter(
                name="sort_by",
                type="string",
                description="Сортировка: 'revenue' (по выручке) или 'cpm' (по CPM)",
                required=False,
                default="revenue"
            )
        ]
    
    def execute(self, limit: int = 15, sort_by: str = "revenue", **kwargs) -> Dict[str, Any]:
        return self.analytics.get_country_stats(limit=limit, sort_by=sort_by)


class CountryStatsTool(BaseTool):
    """Get country × platform CPM analysis"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_country_platform_cpm"
    
    @property
    def description(self) -> str:
        return "Получить CPM по комбинациям страна × платформа. Показывает лучшие комбинации по CPM"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество комбинаций (1-50)",
                required=False,
                default=20
            )
        ]
    
    def execute(self, limit: int = 20, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_country_platform_cpm(limit=limit)

