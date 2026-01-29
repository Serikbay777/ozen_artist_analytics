"""
Artist analytics tools
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService


class TopArtistsTool(BaseTool):
    """Get top artists by revenue or streams"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_top_artists"
    
    @property
    def description(self) -> str:
        return "Получить топ артистов по выручке или стримам. Показывает выручку, стримы, количество треков, платформ, стран, CPM"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество артистов (1-100)",
                required=False,
                default=20
            ),
            ToolParameter(
                name="metric",
                type="string",
                description="Сортировка: 'revenue' (по выручке) или 'streams' (по стримам)",
                required=False,
                default="revenue"
            )
        ]
    
    def execute(self, limit: int = 20, metric: str = "revenue", artist_name: str = None, **kwargs) -> Dict[str, Any]:
        result = self.analytics.get_top_artists(limit=limit, metric=metric)
        
        # Если указан артист - фильтруем только его данные
        if artist_name:
            artists = result.get('artists', [])
            filtered = [a for a in artists if artist_name.lower() in a['artist'].lower()]
            if filtered:
                return {"artists": filtered}
            else:
                return {"artists": [], "message": f"Данные для артиста '{artist_name}' не найдены"}
        
        return result


class ArtistGrowthTool(BaseTool):
    """Get artist growth matrix (2023 vs 2024)"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_artist_growth"
    
    @property
    def description(self) -> str:
        return "Получить матрицу роста артистов (2023 vs 2024). Категории: новые звезды, растущие, стабильные, прорыв, растущие, падающие"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество артистов в каждой категории",
                required=False,
                default=20
            )
        ]
    
    def execute(self, limit: int = 20, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_artist_growth_matrix(limit=limit)


class ArtistDetailsTool(BaseTool):
    """Get detailed artist information including diversity"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_artist_details"
    
    @property
    def description(self) -> str:
        return "Получить детальную информацию об артистах: диверсификация по платформам, странам, количество треков"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество артистов",
                required=False,
                default=20
            )
        ]
    
    def execute(self, limit: int = 20, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_artist_diversity(limit=limit)

