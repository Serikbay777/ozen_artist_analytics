"""
Инструменты аналитики артистов для AI агента
Обертки над ArtistAnalyticsTools для использования в ToolAgent
"""

from .base import BaseTool, ToolParameter
from app.tools.artist_analytics_tools import ArtistAnalyticsTools
from typing import Dict, Any
import json


# Инициализируем класс с инструментами
artist_tools = ArtistAnalyticsTools()


class SearchArtistsTool(BaseTool):
    """Инструмент для поиска артистов"""
    
    @property
    def name(self) -> str:
        return "search_artists"
    
    @property
    def description(self) -> str:
        return "Поиск артистов по имени. Используй когда нужно найти артиста или проверить правильность написания имени."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Поисковый запрос - имя или часть имени артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025 (июль-сентябрь), q4_2025 (октябрь-ноябрь), all (все данные)",
                required=False,
                default="q3_2025"
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Максимальное количество результатов",
                required=False,
                default=20
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение поиска артистов"""
        query = kwargs.get("query")
        period = kwargs.get("period", "q3_2025")
        limit = kwargs.get("limit", 20)
        
        return artist_tools.search_artists(query, period, limit)


class ArtistStreamsTool(BaseTool):
    """Инструмент для получения статистики стримов артиста"""
    
    @property
    def name(self) -> str:
        return "get_artist_streams"
    
    @property
    def description(self) -> str:
        return "Получить статистику стримов артиста: общее количество стримов, доход и среднюю цену за стрим."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Точное имя артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025, q4_2025, all",
                required=False,
                default="q3_2025"
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение получения статистики стримов"""
        artist_name = kwargs.get("artist_name")
        period = kwargs.get("period", "q3_2025")
        
        return artist_tools.get_artist_streams(artist_name, period)


class ArtistPlatformsTool(BaseTool):
    """Инструмент для получения статистики по DSP платформам артиста"""
    
    @property
    def name(self) -> str:
        return "get_artist_platforms"
    
    @property
    def description(self) -> str:
        return "Получить статистику по DSP платформам артиста (Spotify, Apple Music, YouTube и т.д.). Показывает на каких платформах артист наиболее популярен."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Точное имя артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025, q4_2025, all",
                required=False,
                default="q3_2025"
            ),
            ToolParameter(
                name="top_n",
                type="integer",
                description="Количество топ платформ для показа",
                required=False,
                default=10
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение получения статистики по платформам"""
        artist_name = kwargs.get("artist_name")
        period = kwargs.get("period", "q3_2025")
        top_n = kwargs.get("top_n", 10)
        
        return artist_tools.get_artist_platforms(artist_name, period, top_n)


class ArtistGeographyTool(BaseTool):
    """Инструмент для получения географической статистики артиста"""
    
    @property
    def name(self) -> str:
        return "get_artist_geography"
    
    @property
    def description(self) -> str:
        return "Получить географическую статистику артиста (демографию). Показывает в каких странах артист наиболее популярен."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Точное имя артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025, q4_2025, all",
                required=False,
                default="q3_2025"
            ),
            ToolParameter(
                name="top_n",
                type="integer",
                description="Количество топ стран для показа",
                required=False,
                default=15
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение получения географической статистики"""
        artist_name = kwargs.get("artist_name")
        period = kwargs.get("period", "q3_2025")
        top_n = kwargs.get("top_n", 15)
        
        return artist_tools.get_artist_geography(artist_name, period, top_n)


class ArtistTracksTool(BaseTool):
    """Инструмент для получения статистики по трекам артиста"""
    
    @property
    def name(self) -> str:
        return "get_artist_tracks"
    
    @property
    def description(self) -> str:
        return "Получить статистику по трекам артиста. Показывает самые популярные треки по доходу."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Точное имя артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025, q4_2025, all",
                required=False,
                default="q3_2025"
            ),
            ToolParameter(
                name="top_n",
                type="integer",
                description="Количество топ треков для показа",
                required=False,
                default=10
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение получения статистики по трекам"""
        artist_name = kwargs.get("artist_name")
        period = kwargs.get("period", "q3_2025")
        top_n = kwargs.get("top_n", 10)
        
        return artist_tools.get_artist_tracks(artist_name, period, top_n)


class ArtistFullAnalyticsTool(BaseTool):
    """Инструмент для получения полной аналитики по артисту"""
    
    @property
    def name(self) -> str:
        return "get_artist_full_analytics"
    
    @property
    def description(self) -> str:
        return "Получить полную аналитику по артисту: стримы, доход, топ платформы, страны и треки. Используй когда нужна комплексная информация об артисте."
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="artist_name",
                type="string",
                description="Точное имя артиста",
                required=True
            ),
            ToolParameter(
                name="period",
                type="string",
                description="Период данных: q3_2025, q4_2025, all",
                required=False,
                default="q3_2025"
            ),
            ToolParameter(
                name="top_n",
                type="integer",
                description="Количество топ элементов для каждой категории",
                required=False,
                default=10
            )
        ]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение получения полной аналитики"""
        artist_name = kwargs.get("artist_name")
        period = kwargs.get("period", "q3_2025")
        top_n = kwargs.get("top_n", 10)
        
        return artist_tools.get_artist_full_analytics(artist_name, period, top_n)

