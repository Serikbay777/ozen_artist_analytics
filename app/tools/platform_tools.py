"""
Platform analytics tools
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService


class TopPlatformsTool(BaseTool):
    """Get top platforms by revenue"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_top_platforms"
    
    @property
    def description(self) -> str:
        return "Получить топ платформ по выручке. Показывает платформу, выручку, процент от общей выручки, стримы, CPM"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество платформ (1-50)",
                required=False,
                default=15
            )
        ]
    
    def execute(self, limit: int = 15, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_platform_stats(limit=limit)


class PlatformStatsTool(BaseTool):
    """Get platform growth statistics"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_platform_growth"
    
    @property
    def description(self) -> str:
        return "Получить статистику роста платформ (2023 vs 2024). Показывает рост выручки по годам"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_platform_growth()

