"""
Overview and trends analytics tools
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolParameter
from app.services.analytics_service import AnalyticsService


class OverviewStatsTool(BaseTool):
    """Get high-level overview statistics"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_overview_stats"
    
    @property
    def description(self) -> str:
        return "Получить общую статистику: общая выручка, количество стримов, артистов, треков, платформ, стран, средний CPM, период данных"
    
    def execute(self, artist_name: str = None, **kwargs) -> Dict[str, Any]:
        # Если указан артист - возвращаем его статистику
        if artist_name:
            df = self.analytics.df
            artist_df = df[df['Исполнитель'].str.contains(artist_name, case=False, na=False)]
            
            if len(artist_df) == 0:
                return {"message": f"Данные для артиста '{artist_name}' не найдены"}
            
            return {
                "artist": artist_name,
                "total_revenue": float(artist_df['Сумма вознаграждения'].sum()),
                "total_streams": int(artist_df['Количество'].sum()),
                "total_tracks": int(artist_df['Название трека'].nunique()),
                "total_platforms": int(artist_df['Платформа'].nunique()),
                "total_countries": int(artist_df['страна / регион'].nunique()),
                "avg_cpm": float((artist_df['Сумма вознаграждения'].sum() / artist_df['Количество'].sum() * 1000) if artist_df['Количество'].sum() > 0 else 0),
                "date_range": {
                    "from": artist_df['Месяц отчета'].min().isoformat() if len(artist_df) > 0 else None,
                    "to": artist_df['Месяц отчета'].max().isoformat() if len(artist_df) > 0 else None
                },
                "currency": "EUR"
            }
        
        return self.analytics.get_overview_stats()


class TrendsTool(BaseTool):
    """Get trends (yearly, monthly, quarterly)"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    @property
    def name(self) -> str:
        return "get_trends"
    
    @property
    def description(self) -> str:
        return "Получить тренды по периодам: годовые (с ростом YoY), месячные, квартальные. Можно указать тип тренда и год для фильтрации"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="trend_type",
                type="string",
                description="Тип тренда: 'yearly' (годовые), 'monthly' (месячные), 'quarterly' (квартальные)",
                required=False,
                default="yearly"
            ),
            ToolParameter(
                name="year",
                type="integer",
                description="Год для фильтрации (только для monthly)",
                required=False,
                default=None
            )
        ]
    
    def execute(self, trend_type: str = "yearly", year: int = None, **kwargs) -> Dict[str, Any]:
        if trend_type == "yearly":
            return self.analytics.get_yearly_trends()
        elif trend_type == "monthly":
            return self.analytics.get_monthly_trends(year=year)
        elif trend_type == "quarterly":
            return self.analytics.get_quarterly_trends()
        else:
            return {"error": f"Unknown trend_type: {trend_type}"}

