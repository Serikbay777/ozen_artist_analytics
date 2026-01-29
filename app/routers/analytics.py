"""
Analytics API Router
Provides comprehensive analytics endpoints for frontend visualization
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.analytics_service import AnalyticsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize analytics service
try:
    analytics_service = AnalyticsService()
    logger.info("✅ Analytics service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize analytics service: {str(e)}")
    analytics_service = None


@router.get("/overview")
async def get_overview():
    """
    Get high-level overview statistics
    
    Returns:
    - total_revenue: Total revenue in EUR
    - total_streams: Total number of streams
    - total_artists: Number of unique artists
    - total_tracks: Number of unique tracks
    - total_platforms: Number of platforms
    - total_countries: Number of countries
    - avg_cpm: Average CPM (cost per 1000 streams)
    - date_range: Data date range
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_overview_stats()
    except Exception as e:
        logger.error(f"Error in get_overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/yearly")
async def get_yearly_trends():
    """
    Get year-over-year trends
    
    Returns yearly data with:
    - revenue, streams, artists count
    - YoY growth percentages
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_yearly_trends()
    except Exception as e:
        logger.error(f"Error in get_yearly_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/monthly")
async def get_monthly_trends(year: Optional[int] = Query(None, description="Filter by year")):
    """
    Get monthly trends, optionally filtered by year
    
    Parameters:
    - year: Optional year filter
    
    Returns monthly data with revenue, streams, and CPM
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_monthly_trends(year=year)
    except Exception as e:
        logger.error(f"Error in get_monthly_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/quarterly")
async def get_quarterly_trends():
    """
    Get quarterly trends
    
    Returns quarterly revenue and streams data
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_quarterly_trends()
    except Exception as e:
        logger.error(f"Error in get_quarterly_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/top")
async def get_top_artists(
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    metric: str = Query("revenue", regex="^(revenue|streams)$", description="Sort by revenue or streams")
):
    """
    Get top artists by revenue or streams
    
    Parameters:
    - limit: Number of artists to return (1-100)
    - metric: Sort by 'revenue' or 'streams'
    
    Returns artist data with revenue, streams, tracks, platforms, countries, CPM
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_top_artists(limit=limit, metric=metric)
    except Exception as e:
        logger.error(f"Error in get_top_artists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/growth")
async def get_artist_growth(limit: int = Query(20, ge=1, le=100)):
    """
    Get artist growth matrix (2023 vs 2024)
    
    Categorizes artists into:
    - new_star: New artists in 2024
    - rising_star: High revenue with >50% growth
    - stable_star: High revenue with positive growth
    - breakthrough: Medium revenue with >100% growth
    - growing: Positive growth
    - declining: Negative growth
    
    Parameters:
    - limit: Number of artists per category
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_artist_growth_matrix(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_artist_growth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artists/diversity")
async def get_artist_diversity(limit: int = Query(20, ge=1, le=100)):
    """
    Get artist diversification metrics
    
    Shows how diversified each artist is across:
    - Platforms
    - Countries
    - Tracks
    
    Parameters:
    - limit: Number of artists to return
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_artist_diversity(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_artist_diversity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracks/top")
async def get_top_tracks(
    limit: int = Query(20, ge=1, le=100),
    metric: str = Query("revenue", regex="^(revenue|streams)$")
):
    """
    Get top tracks by revenue or streams
    
    Parameters:
    - limit: Number of tracks to return (1-100)
    - metric: Sort by 'revenue' or 'streams'
    
    Returns track data with artist, revenue, streams, CPM
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_top_tracks(limit=limit, metric=metric)
    except Exception as e:
        logger.error(f"Error in get_top_tracks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracks/lifecycle")
async def get_track_lifecycle(limit: int = Query(15, ge=1, le=50)):
    """
    Get track lifecycle analysis
    
    Returns:
    - long_running: Tracks active for the most months
    - most_profitable_per_month: Tracks with highest monthly revenue
    
    Parameters:
    - limit: Number of tracks per category
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_track_lifecycle(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_track_lifecycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def get_platform_stats(limit: int = Query(15, ge=1, le=50)):
    """
    Get platform statistics
    
    Returns platform data with revenue, streams, CPM
    
    Parameters:
    - limit: Number of platforms to return
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_platform_stats(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_platform_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms/growth")
async def get_platform_growth():
    """
    Get platform growth trends (2023 vs 2024)
    
    Returns platforms with year-over-year growth data
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_platform_growth()
    except Exception as e:
        logger.error(f"Error in get_platform_growth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/countries")
async def get_country_stats(
    limit: int = Query(15, ge=1, le=50),
    sort_by: str = Query("revenue", regex="^(revenue|cpm)$")
):
    """
    Get country statistics
    
    Parameters:
    - limit: Number of countries to return
    - sort_by: Sort by 'revenue' or 'cpm'
    
    Returns country data with revenue, streams, CPM
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_country_stats(limit=limit, sort_by=sort_by)
    except Exception as e:
        logger.error(f"Error in get_country_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/countries/platform-cpm")
async def get_country_platform_cpm(limit: int = Query(20, ge=1, le=50)):
    """
    Get CPM by country × platform combination
    
    Shows the best performing country-platform combinations by CPM
    
    Parameters:
    - limit: Number of combinations to return
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_country_platform_cpm(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_country_platform_cpm: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concentration")
async def get_revenue_concentration():
    """
    Get revenue concentration analysis
    
    Shows how revenue is concentrated among:
    - Top 10, 20, 50 artists
    - Top 10, 50, 100 tracks
    
    Useful for understanding catalog dependency
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_revenue_concentration()
    except Exception as e:
        logger.error(f"Error in get_revenue_concentration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels")
async def get_label_stats(limit: int = Query(10, ge=1, le=50)):
    """
    Get label statistics
    
    Returns label data with revenue, artists, tracks, CPM, revenue per artist
    
    Parameters:
    - limit: Number of labels to return
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_label_stats(limit=limit)
    except Exception as e:
        logger.error(f"Error in get_label_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sale-types")
async def get_sale_type_stats():
    """
    Get sale type statistics
    
    Returns distribution of revenue and streams by sale type
    (e.g., streaming, download, etc.) with CPM
    """
    if not analytics_service:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    
    try:
        return analytics_service.get_sale_type_stats()
    except Exception as e:
        logger.error(f"Error in get_sale_type_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

