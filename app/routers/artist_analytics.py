"""
API для аналитики по артистам
Эндпоинты для получения стримов, демографии и DSP статистики
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/artists", tags=["Artist Analytics"])


# Модели данных
class StreamStats(BaseModel):
    """Статистика стримов"""
    total_streams: int
    total_revenue: float
    average_per_stream: float
    period: str


class PlatformStats(BaseModel):
    """Статистика по платформе"""
    platform: str
    streams: int
    revenue: float
    percentage: float


class CountryStats(BaseModel):
    """Статистика по стране"""
    country: str
    streams: int
    revenue: float
    percentage: float


class TrackStats(BaseModel):
    """Статистика по треку"""
    track_name: str
    streams: int
    revenue: float
    percentage: float


class ArtistAnalytics(BaseModel):
    """Полная аналитика по артисту"""
    artist_name: str
    period: str
    total_streams: int
    total_revenue: float
    total_tracks: int
    top_platforms: List[PlatformStats]
    top_countries: List[CountryStats]
    top_tracks: List[TrackStats]


class ArtistHelper:
    """Вспомогательный класс для работы с данными артистов"""
    
    @staticmethod
    def load_data(period: str = "q3_2025") -> pd.DataFrame:
        """
        Загрузка данных за период
        
        Args:
            period: Период данных (q3_2025, q4_2025, all)
        """
        data_dir = Path("data/processed")
        
        # Маппинг периодов на файлы
        period_files = {
            "q3_2025": "1740260_704133_2025-07-01_2025-09-01.csv",
            "q4_2025": "1855874_704133_2025-10-01_2025-12-01.csv",  # Актуальный файл Q4 2025
            "q4_2025_oct": "1787646_704133_2025-10-01_2025-10-01 2.csv",
            "q4_2025_nov": "1821306_704133_2025-11-01_2025-11-01.csv",
        }
        
        if period == "all":
            # Загружаем все файлы
            dfs = []
            for file_name in period_files.values():
                file_path = data_dir / file_name
                if file_path.exists():
                    df = pd.read_csv(file_path, sep=';', encoding='utf-8', quotechar='"', low_memory=False)
                    dfs.append(df)
            
            if not dfs:
                raise HTTPException(status_code=404, detail="Данные не найдены")
            
            return pd.concat(dfs, ignore_index=True)
        
        else:
            # Загружаем конкретный файл
            if period not in period_files:
                raise HTTPException(status_code=400, detail=f"Неизвестный период: {period}")
            
            file_path = data_dir / period_files[period]
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"Файл не найден: {file_path}")
            
            return pd.read_csv(file_path, sep=';', encoding='utf-8', quotechar='"', low_memory=False)
    
    @staticmethod
    def clean_numeric(df: pd.DataFrame, column: str) -> pd.Series:
        """Очистка числовых колонок"""
        if column not in df.columns:
            return pd.Series([0] * len(df))
        return df[column].astype(str).str.replace(',', '.').astype(float)
    
    @staticmethod
    def get_artist_data(df: pd.DataFrame, artist_name: str) -> pd.DataFrame:
        """Получение данных по артисту"""
        artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
        
        # Фильтруем по артисту (регистронезависимый поиск)
        artist_df = df[df[artist_col].str.lower() == artist_name.lower()]
        
        if artist_df.empty:
            raise HTTPException(status_code=404, detail=f"Артист '{artist_name}' не найден")
        
        return artist_df


@router.get("/search")
async def search_artists(
    query: str = Query(..., min_length=2, description="Поисковый запрос (минимум 2 символа)"),
    period: str = Query("q3_2025", description="Период данных (q3_2025, q4_2025, all)"),
    limit: int = Query(20, ge=1, le=100, description="Максимум результатов")
):
    """
    Поиск артистов по имени
    
    Возвращает список артистов, соответствующих поисковому запросу
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
        
        # Поиск артистов (регистронезависимый)
        matching_artists = df[df[artist_col].str.contains(query, case=False, na=False)][artist_col].unique()
        
        # Ограничиваем количество результатов
        matching_artists = matching_artists[:limit]
        
        return {
            "query": query,
            "period": period,
            "count": len(matching_artists),
            "artists": matching_artists.tolist()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("/{artist_name}/streams")
async def get_artist_streams(
    artist_name: str,
    period: str = Query("q3_2025", description="Период данных (q3_2025, q4_2025, all)")
):
    """
    Получить статистику стримов артиста
    
    Возвращает общее количество стримов, доход и среднюю цену за стрим
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_df = ArtistHelper.get_artist_data(df, artist_name)
        
        # Очищаем числовые колонки
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        
        artist_df['revenue_clean'] = ArtistHelper.clean_numeric(artist_df, revenue_col)
        artist_df['quantity_clean'] = ArtistHelper.clean_numeric(artist_df, quantity_col)
        
        total_streams = int(artist_df['quantity_clean'].sum())
        total_revenue = round(artist_df['revenue_clean'].sum(), 2)
        avg_per_stream = round(total_revenue / total_streams, 6) if total_streams > 0 else 0
        
        return StreamStats(
            total_streams=total_streams,
            total_revenue=total_revenue,
            average_per_stream=avg_per_stream,
            period=period
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения стримов: {str(e)}")


@router.get("/{artist_name}/platforms")
async def get_artist_platforms(
    artist_name: str,
    period: str = Query("q3_2025", description="Период данных"),
    top_n: int = Query(10, ge=1, le=50, description="Количество топ платформ")
):
    """
    Получить статистику по DSP платформам артиста
    
    Возвращает топ платформ по доходу с процентами
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_df = ArtistHelper.get_artist_data(df, artist_name)
        
        # Колонки
        platform_col = 'Платформа' if 'Платформа' in df.columns else 'Platform'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        
        # Очищаем числовые колонки
        artist_df['revenue_clean'] = ArtistHelper.clean_numeric(artist_df, revenue_col)
        artist_df['quantity_clean'] = ArtistHelper.clean_numeric(artist_df, quantity_col)
        
        # Группируем по платформам
        platform_stats = artist_df.groupby(platform_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).round(2)
        
        platform_stats = platform_stats.sort_values('revenue_clean', ascending=False).head(top_n)
        
        total_revenue = artist_df['revenue_clean'].sum()
        
        # Формируем результат
        platforms = []
        for platform, row in platform_stats.iterrows():
            platforms.append(PlatformStats(
                platform=platform,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
            ))
        
        return {
            "artist": artist_name,
            "period": period,
            "total_platforms": len(artist_df[platform_col].unique()),
            "top_platforms": platforms
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения платформ: {str(e)}")


@router.get("/{artist_name}/geography")
async def get_artist_geography(
    artist_name: str,
    period: str = Query("q3_2025", description="Период данных"),
    top_n: int = Query(15, ge=1, le=50, description="Количество топ стран")
):
    """
    Получить географическую статистику артиста (демографию)
    
    Возвращает топ стран по доходу с процентами
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_df = ArtistHelper.get_artist_data(df, artist_name)
        
        # Колонки
        country_col = 'страна / регион' if 'страна / регион' in df.columns else 'Country'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        
        # Очищаем числовые колонки
        artist_df['revenue_clean'] = ArtistHelper.clean_numeric(artist_df, revenue_col)
        artist_df['quantity_clean'] = ArtistHelper.clean_numeric(artist_df, quantity_col)
        
        # Группируем по странам
        country_stats = artist_df.groupby(country_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).round(2)
        
        country_stats = country_stats.sort_values('revenue_clean', ascending=False).head(top_n)
        
        total_revenue = artist_df['revenue_clean'].sum()
        
        # Формируем результат
        countries = []
        for country, row in country_stats.iterrows():
            countries.append(CountryStats(
                country=country,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
            ))
        
        return {
            "artist": artist_name,
            "period": period,
            "total_countries": len(artist_df[country_col].unique()),
            "top_countries": countries
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения географии: {str(e)}")


@router.get("/{artist_name}/tracks")
async def get_artist_tracks(
    artist_name: str,
    period: str = Query("q3_2025", description="Период данных"),
    top_n: int = Query(10, ge=1, le=50, description="Количество топ треков")
):
    """
    Получить статистику по трекам артиста
    
    Возвращает топ треков по доходу с процентами
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_df = ArtistHelper.get_artist_data(df, artist_name)
        
        # Колонки
        track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        
        # Очищаем числовые колонки
        artist_df['revenue_clean'] = ArtistHelper.clean_numeric(artist_df, revenue_col)
        artist_df['quantity_clean'] = ArtistHelper.clean_numeric(artist_df, quantity_col)
        
        # Группируем по трекам
        track_stats = artist_df.groupby(track_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).round(2)
        
        track_stats = track_stats.sort_values('revenue_clean', ascending=False).head(top_n)
        
        total_revenue = artist_df['revenue_clean'].sum()
        
        # Формируем результат
        tracks = []
        for track, row in track_stats.iterrows():
            tracks.append(TrackStats(
                track_name=track,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
            ))
        
        return {
            "artist": artist_name,
            "period": period,
            "total_tracks": len(artist_df[track_col].unique()),
            "top_tracks": tracks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения треков: {str(e)}")


@router.get("/{artist_name}/analytics")
async def get_artist_full_analytics(
    artist_name: str,
    period: str = Query("q3_2025", description="Период данных"),
    top_n: int = Query(10, ge=1, le=20, description="Количество топ элементов")
):
    """
    Получить полную аналитику по артисту
    
    Возвращает все данные: стримы, топ платформы, страны и треки
    """
    try:
        df = ArtistHelper.load_data(period)
        artist_df = ArtistHelper.get_artist_data(df, artist_name)
        
        # Колонки
        platform_col = 'Платформа' if 'Платформа' in df.columns else 'Platform'
        country_col = 'страна / регион' if 'страна / регион' in df.columns else 'Country'
        track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        
        # Очищаем числовые колонки
        artist_df['revenue_clean'] = ArtistHelper.clean_numeric(artist_df, revenue_col)
        artist_df['quantity_clean'] = ArtistHelper.clean_numeric(artist_df, quantity_col)
        
        total_streams = int(artist_df['quantity_clean'].sum())
        total_revenue = round(artist_df['revenue_clean'].sum(), 2)
        total_tracks = len(artist_df[track_col].unique())
        
        # Топ платформы
        platform_stats = artist_df.groupby(platform_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).sort_values('revenue_clean', ascending=False).head(top_n)
        
        top_platforms = [
            PlatformStats(
                platform=platform,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2)
            )
            for platform, row in platform_stats.iterrows()
        ]
        
        # Топ страны
        country_stats = artist_df.groupby(country_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).sort_values('revenue_clean', ascending=False).head(top_n)
        
        top_countries = [
            CountryStats(
                country=country,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2)
            )
            for country, row in country_stats.iterrows()
        ]
        
        # Топ треки
        track_stats = artist_df.groupby(track_col).agg({
            'quantity_clean': 'sum',
            'revenue_clean': 'sum'
        }).sort_values('revenue_clean', ascending=False).head(top_n)
        
        top_tracks = [
            TrackStats(
                track_name=track,
                streams=int(row['quantity_clean']),
                revenue=float(row['revenue_clean']),
                percentage=round((row['revenue_clean'] / total_revenue * 100), 2)
            )
            for track, row in track_stats.iterrows()
        ]
        
        return ArtistAnalytics(
            artist_name=artist_name,
            period=period,
            total_streams=total_streams,
            total_revenue=total_revenue,
            total_tracks=total_tracks,
            top_platforms=top_platforms,
            top_countries=top_countries,
            top_tracks=top_tracks
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения аналитики: {str(e)}")

