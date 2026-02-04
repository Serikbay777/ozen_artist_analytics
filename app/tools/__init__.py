"""
Analytics Tools for AI Agent
Each tool provides specific analytics functionality
"""

from .base import BaseTool
from .platform_tools import PlatformStatsTool, TopPlatformsTool
from .artist_tools import TopArtistsTool, ArtistGrowthTool, ArtistDetailsTool
from .track_tools import TopTracksTool, TrackDetailsTool
from .country_tools import TopCountriesTool, CountryStatsTool
from .overview_tools import OverviewStatsTool, TrendsTool
from .artist_analytics_agent_tools import (
    SearchArtistsTool,
    ArtistStreamsTool,
    ArtistPlatformsTool,
    ArtistGeographyTool,
    ArtistTracksTool,
    ArtistFullAnalyticsTool
)
from .report_generation_tools import GenerateArtistReportTool

# Список всех доступных инструментов
ALL_TOOLS = [
    OverviewStatsTool(),
    TrendsTool(),
    TopArtistsTool(),
    ArtistGrowthTool(),
    ArtistDetailsTool(),
    TopTracksTool(),
    TrackDetailsTool(),
    TopPlatformsTool(),
    PlatformStatsTool(),
    TopCountriesTool(),
    CountryStatsTool(),
    # Новые инструменты для детальной аналитики артистов
    SearchArtistsTool(),
    ArtistStreamsTool(),
    ArtistPlatformsTool(),
    ArtistGeographyTool(),
    ArtistTracksTool(),
    ArtistFullAnalyticsTool(),
    # Генерация PDF-отчетов
    GenerateArtistReportTool(),
]

__all__ = [
    'BaseTool',
    'ALL_TOOLS',
    'OverviewStatsTool',
    'TrendsTool',
    'TopArtistsTool',
    'ArtistGrowthTool',
    'ArtistDetailsTool',
    'TopTracksTool',
    'TrackDetailsTool',
    'TopPlatformsTool',
    'PlatformStatsTool',
    'TopCountriesTool',
    'CountryStatsTool',
]

