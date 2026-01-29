"""
Инструменты для аналитики артистов
Используются AI агентом для получения данных о стримах, демографии и DSP
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import json


class ArtistAnalyticsTools:
    """Набор инструментов для аналитики артистов"""
    
    def __init__(self, data_dir: str = "data/processed"):
        """
        Инициализация инструментов
        
        Args:
            data_dir: Путь к директории с данными
        """
        self.data_dir = Path(data_dir)
        self.period_files = {
            "q3_2025": "1740260_704133_2025-07-01_2025-09-01.csv",
            "q4_2025_oct": "1787646_704133_2025-10-01_2025-10-01 2.csv",
            "q4_2025_nov": "1821306_704133_2025-11-01_2025-11-01.csv",
        }
    
    def _load_data(self, period: str = "q3_2025") -> pd.DataFrame:
        """Загрузка данных за период"""
        if period == "all":
            dfs = []
            for file_name in self.period_files.values():
                file_path = self.data_dir / file_name
                if file_path.exists():
                    df = pd.read_csv(file_path, sep=';', encoding='utf-8', quotechar='"', low_memory=False)
                    dfs.append(df)
            return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
        elif period == "q4_2025":
            dfs = []
            for key in ["q4_2025_oct", "q4_2025_nov"]:
                file_path = self.data_dir / self.period_files[key]
                if file_path.exists():
                    df = pd.read_csv(file_path, sep=';', encoding='utf-8', quotechar='"', low_memory=False)
                    dfs.append(df)
            return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
        else:
            if period not in self.period_files:
                return pd.DataFrame()
            
            file_path = self.data_dir / self.period_files[period]
            if not file_path.exists():
                return pd.DataFrame()
            
            return pd.read_csv(file_path, sep=';', encoding='utf-8', quotechar='"', low_memory=False)
    
    def _clean_numeric(self, df: pd.DataFrame, column: str) -> pd.Series:
        """Очистка числовых колонок"""
        if column not in df.columns:
            return pd.Series([0] * len(df))
        return df[column].astype(str).str.replace(',', '.').astype(float)
    
    def _get_artist_data(self, df: pd.DataFrame, artist_name: str) -> pd.DataFrame:
        """Получение данных по артисту"""
        artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
        return df[df[artist_col].str.lower() == artist_name.lower()]
    
    def search_artists(self, query: str, period: str = "q3_2025", limit: int = 20) -> Dict[str, Any]:
        """
        Поиск артистов по имени
        
        Args:
            query: Поисковый запрос (минимум 2 символа)
            period: Период данных (q3_2025, q4_2025, all)
            limit: Максимум результатов
            
        Returns:
            Словарь с найденными артистами
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены", "artists": []}
            
            artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
            matching_artists = df[df[artist_col].str.contains(query, case=False, na=False)][artist_col].unique()
            matching_artists = matching_artists[:limit]
            
            return {
                "query": query,
                "period": period,
                "count": len(matching_artists),
                "artists": matching_artists.tolist()
            }
        except Exception as e:
            return {"error": str(e), "artists": []}
    
    def get_artist_streams(self, artist_name: str, period: str = "q3_2025") -> Dict[str, Any]:
        """
        Получить статистику стримов артиста
        
        Args:
            artist_name: Имя артиста
            period: Период данных (q3_2025, q4_2025, all)
            
        Returns:
            Словарь со статистикой стримов
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены"}
            
            artist_df = self._get_artist_data(df, artist_name)
            if artist_df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
            quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
            
            artist_df['revenue_clean'] = self._clean_numeric(artist_df, revenue_col)
            artist_df['quantity_clean'] = self._clean_numeric(artist_df, quantity_col)
            
            total_streams = int(artist_df['quantity_clean'].sum())
            total_revenue = round(artist_df['revenue_clean'].sum(), 2)
            avg_per_stream = round(total_revenue / total_streams, 6) if total_streams > 0 else 0
            
            return {
                "artist": artist_name,
                "period": period,
                "total_streams": total_streams,
                "total_revenue": total_revenue,
                "average_per_stream": avg_per_stream,
                "currency": "EUR"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_platforms(self, artist_name: str, period: str = "q3_2025", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить статистику по DSP платформам артиста
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ платформ
            
        Returns:
            Словарь со статистикой по платформам
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены"}
            
            artist_df = self._get_artist_data(df, artist_name)
            if artist_df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            platform_col = 'Платформа' if 'Платформа' in df.columns else 'Platform'
            revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
            quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
            
            artist_df['revenue_clean'] = self._clean_numeric(artist_df, revenue_col)
            artist_df['quantity_clean'] = self._clean_numeric(artist_df, quantity_col)
            
            platform_stats = artist_df.groupby(platform_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).round(2)
            
            platform_stats = platform_stats.sort_values('revenue_clean', ascending=False).head(top_n)
            total_revenue = artist_df['revenue_clean'].sum()
            
            platforms = []
            for platform, row in platform_stats.iterrows():
                platforms.append({
                    "platform": platform,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            return {
                "artist": artist_name,
                "period": period,
                "total_platforms": len(artist_df[platform_col].unique()),
                "top_platforms": platforms
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_geography(self, artist_name: str, period: str = "q3_2025", top_n: int = 15) -> Dict[str, Any]:
        """
        Получить географическую статистику артиста (демографию)
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ стран
            
        Returns:
            Словарь с географической статистикой
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены"}
            
            artist_df = self._get_artist_data(df, artist_name)
            if artist_df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            country_col = 'страна / регион' if 'страна / регион' in df.columns else 'Country'
            revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
            quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
            
            artist_df['revenue_clean'] = self._clean_numeric(artist_df, revenue_col)
            artist_df['quantity_clean'] = self._clean_numeric(artist_df, quantity_col)
            
            country_stats = artist_df.groupby(country_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).round(2)
            
            country_stats = country_stats.sort_values('revenue_clean', ascending=False).head(top_n)
            total_revenue = artist_df['revenue_clean'].sum()
            
            countries = []
            for country, row in country_stats.iterrows():
                countries.append({
                    "country": country,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            return {
                "artist": artist_name,
                "period": period,
                "total_countries": len(artist_df[country_col].unique()),
                "top_countries": countries
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_tracks(self, artist_name: str, period: str = "q3_2025", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить статистику по трекам артиста
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ треков
            
        Returns:
            Словарь со статистикой по трекам
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены"}
            
            artist_df = self._get_artist_data(df, artist_name)
            if artist_df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
            revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
            quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
            
            artist_df['revenue_clean'] = self._clean_numeric(artist_df, revenue_col)
            artist_df['quantity_clean'] = self._clean_numeric(artist_df, quantity_col)
            
            track_stats = artist_df.groupby(track_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).round(2)
            
            track_stats = track_stats.sort_values('revenue_clean', ascending=False).head(top_n)
            total_revenue = artist_df['revenue_clean'].sum()
            
            tracks = []
            for track, row in track_stats.iterrows():
                tracks.append({
                    "track_name": track,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            return {
                "artist": artist_name,
                "period": period,
                "total_tracks": len(artist_df[track_col].unique()),
                "top_tracks": tracks
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_full_analytics(self, artist_name: str, period: str = "q3_2025", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить полную аналитику по артисту
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ элементов
            
        Returns:
            Словарь с полной аналитикой
        """
        try:
            df = self._load_data(period)
            if df.empty:
                return {"error": "Данные не найдены"}
            
            artist_df = self._get_artist_data(df, artist_name)
            if artist_df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            # Колонки
            platform_col = 'Платформа' if 'Платформа' in df.columns else 'Platform'
            country_col = 'страна / регион' if 'страна / регион' in df.columns else 'Country'
            track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
            revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
            quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
            
            # Очищаем числовые колонки
            artist_df['revenue_clean'] = self._clean_numeric(artist_df, revenue_col)
            artist_df['quantity_clean'] = self._clean_numeric(artist_df, quantity_col)
            
            total_streams = int(artist_df['quantity_clean'].sum())
            total_revenue = round(artist_df['revenue_clean'].sum(), 2)
            total_tracks = len(artist_df[track_col].unique())
            
            # Топ платформы
            platform_stats = artist_df.groupby(platform_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).sort_values('revenue_clean', ascending=False).head(top_n)
            
            top_platforms = [
                {
                    "platform": platform,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2)
                }
                for platform, row in platform_stats.iterrows()
            ]
            
            # Топ страны
            country_stats = artist_df.groupby(country_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).sort_values('revenue_clean', ascending=False).head(top_n)
            
            top_countries = [
                {
                    "country": country,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2)
                }
                for country, row in country_stats.iterrows()
            ]
            
            # Топ треки
            track_stats = artist_df.groupby(track_col).agg({
                'quantity_clean': 'sum',
                'revenue_clean': 'sum'
            }).sort_values('revenue_clean', ascending=False).head(top_n)
            
            top_tracks = [
                {
                    "track_name": track,
                    "streams": int(row['quantity_clean']),
                    "revenue": float(row['revenue_clean']),
                    "percentage": round((row['revenue_clean'] / total_revenue * 100), 2)
                }
                for track, row in track_stats.iterrows()
            ]
            
            return {
                "artist_name": artist_name,
                "period": period,
                "total_streams": total_streams,
                "total_revenue": total_revenue,
                "total_tracks": total_tracks,
                "currency": "EUR",
                "top_platforms": top_platforms,
                "top_countries": top_countries,
                "top_tracks": top_tracks
            }
        except Exception as e:
            return {"error": str(e)}


# Определения инструментов для AI агента
ARTIST_ANALYTICS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_artists",
            "description": "Поиск артистов по имени. Используй когда нужно найти артиста или проверить правильность написания имени.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос - имя или часть имени артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных: q3_2025 (июль-сентябрь), q4_2025 (октябрь-ноябрь), all (все данные)",
                        "default": "q3_2025"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество результатов",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_artist_streams",
            "description": "Получить статистику стримов артиста: общее количество стримов, доход и среднюю цену за стрим.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Точное имя артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных",
                        "default": "q3_2025"
                    }
                },
                "required": ["artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_artist_platforms",
            "description": "Получить статистику по DSP платформам артиста (Spotify, Apple Music, YouTube и т.д.). Показывает на каких платформах артист наиболее популярен.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Точное имя артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных",
                        "default": "q3_2025"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Количество топ платформ для показа",
                        "default": 10
                    }
                },
                "required": ["artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_artist_geography",
            "description": "Получить географическую статистику артиста (демографию). Показывает в каких странах артист наиболее популярен.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Точное имя артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных",
                        "default": "q3_2025"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Количество топ стран для показа",
                        "default": 15
                    }
                },
                "required": ["artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_artist_tracks",
            "description": "Получить статистику по трекам артиста. Показывает самые популярные треки по доходу.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Точное имя артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных",
                        "default": "q3_2025"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Количество топ треков для показа",
                        "default": 10
                    }
                },
                "required": ["artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_artist_full_analytics",
            "description": "Получить полную аналитику по артисту: стримы, доход, топ платформы, страны и треки. Используй когда нужна комплексная информация об артисте.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Точное имя артиста"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["q3_2025", "q4_2025", "all"],
                        "description": "Период данных",
                        "default": "q3_2025"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Количество топ элементов для каждой категории",
                        "default": 10
                    }
                },
                "required": ["artist_name"]
            }
        }
    }
]

