"""
Track analytics tools
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService


class TopTracksTool(BaseTool):
    """Get top tracks by revenue or streams"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_top_tracks"
    
    @property
    def description(self) -> str:
        return "Получить топ треков по выручке или стримам. Показывает артиста, название трека, выручку, стримы, CPM"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество треков (1-100)",
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
        result = self.analytics.get_top_tracks(limit=limit, metric=metric)
        
        # Если указан артист - фильтруем только его треки
        if artist_name:
            tracks = result.get('tracks', [])
            filtered = [t for t in tracks if artist_name.lower() in t['artist'].lower()]
            if filtered:
                return {"tracks": filtered}
            else:
                return {"tracks": [], "message": f"Треки артиста '{artist_name}' не найдены"}
        
        return result


class TrackDetailsTool(BaseTool):
    """Get track lifecycle analysis"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_track_lifecycle"
    
    @property
    def description(self) -> str:
        return "Получить анализ жизненного цикла треков: долгоиграющие треки (evergreen) и самые прибыльные в месяц"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="limit",
                type="integer",
                description="Количество треков в каждой категории",
                required=False,
                default=15
            )
        ]
    
    def execute(self, limit: int = 15, **kwargs) -> Dict[str, Any]:
        return self.analytics.get_track_lifecycle(limit=limit)

