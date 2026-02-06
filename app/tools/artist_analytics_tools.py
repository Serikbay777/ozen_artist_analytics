"""
Инструменты для аналитики артистов
Используются AI агентом для получения данных о стримах, демографии и DSP
SQLite версия для оптимизации памяти
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import json


class ArtistAnalyticsTools:
    """Набор инструментов для аналитики артистов (SQLite версия)"""
    
    def __init__(self, db_path: str = None):
        """
        Инициализация инструментов
        
        Args:
            db_path: Путь к SQLite базе данных
        """
        if db_path is None:
            base_dir = Path(__file__).parent.parent.parent
            db_path = str(base_dir / 'data' / 'analytics.db')
        
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"SQLite database not found at {self.db_path}. Please run scripts/csv_to_sqlite.py first.")
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ ArtistAnalyticsTools initialized with SQLite from {self.db_path}")
    
    def _load_data(self, period: str = "all", artist_name: str = None) -> pd.DataFrame:
        """
        Загрузка данных за период из SQLite
        
        Args:
            period: Период данных (q3_2025, q4_2025, all)
            artist_name: Имя артиста для фильтрации (опционально)
        """
        query = "SELECT * FROM analytics WHERE 1=1"
        params = []
        
        # Фильтр по периоду
        if period == "q3_2025":
            query += " AND year = 2025 AND quarter = 3"
        elif period == "q4_2025":
            query += " AND year = 2025 AND quarter = 4"
        # period == "all" - без фильтра
        
        # Фильтр по артисту
        if artist_name:
            query += " AND LOWER(Исполнитель) = LOWER(?)"
            params.append(artist_name)
        
        return pd.read_sql(query, self.conn, params=params if params else None)
    
    def search_artists(self, query: str, period: str = "all", limit: int = 20) -> Dict[str, Any]:
        """
        Поиск артистов по имени (SQLite версия)
        
        Args:
            query: Поисковый запрос (минимум 2 символа)
            period: Период данных (q3_2025, q4_2025, all)
            limit: Максимум результатов
            
        Returns:
            Словарь с найденными артистами
        """
        try:
            sql_query = """
                SELECT DISTINCT Исполнитель
                FROM analytics
                WHERE LOWER(Исполнитель) LIKE LOWER(?)
            """
            params = [f"%{query}%"]
            
            # Фильтр по периоду
            if period == "q3_2025":
                sql_query += " AND year = 2025 AND quarter = 3"
            elif period == "q4_2025":
                sql_query += " AND year = 2025 AND quarter = 4"
            
            sql_query += f" LIMIT {limit}"
            
            df = pd.read_sql(sql_query, self.conn, params=params)
            artists = df['Исполнитель'].tolist() if not df.empty else []
            
            return {
                "query": query,
                "period": period,
                "count": len(artists),
                "artists": artists
            }
        except Exception as e:
            return {"error": str(e), "artists": []}
    
    def get_artist_streams(self, artist_name: str, period: str = "all") -> Dict[str, Any]:
        """
        Получить статистику стримов артиста (SQLite версия)
        
        Args:
            artist_name: Имя артиста
            period: Период данных (q3_2025, q4_2025, all)
            
        Returns:
            Словарь со статистикой стримов
        """
        try:
            sql_query = """
                SELECT 
                    SUM(Количество) as total_streams,
                    SUM("Сумма вознаграждения") as total_revenue
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            params = [artist_name]
            
            # Фильтр по периоду
            if period == "q3_2025":
                sql_query += " AND year = 2025 AND quarter = 3"
            elif period == "q4_2025":
                sql_query += " AND year = 2025 AND quarter = 4"
            
            df = pd.read_sql(sql_query, self.conn, params=params)
            
            if df.empty or df['total_streams'].iloc[0] is None:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            total_streams = int(df['total_streams'].iloc[0])
            total_revenue = round(float(df['total_revenue'].iloc[0]), 2)
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
    
    def get_artist_platforms(self, artist_name: str, period: str = "all", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить статистику по DSP платформам артиста (SQLite версия)
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ платформ
            
        Returns:
            Словарь со статистикой по платформам
        """
        try:
            sql_query = """
                SELECT 
                    Платформа as platform,
                    SUM(Количество) as streams,
                    SUM("Сумма вознаграждения") as revenue
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            params = [artist_name]
            
            # Фильтр по периоду
            if period == "q3_2025":
                sql_query += " AND year = 2025 AND quarter = 3"
            elif period == "q4_2025":
                sql_query += " AND year = 2025 AND quarter = 4"
            
            sql_query += f"""
                GROUP BY Платформа
                ORDER BY revenue DESC
                LIMIT {top_n}
            """
            
            df = pd.read_sql(sql_query, self.conn, params=params)
            
            if df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            total_revenue = df['revenue'].sum()
            
            platforms = []
            for _, row in df.iterrows():
                platforms.append({
                    "platform": row['platform'],
                    "streams": int(row['streams']),
                    "revenue": float(row['revenue']),
                    "percentage": round((row['revenue'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            # Получаем общее количество платформ
            total_platforms_query = """
                SELECT COUNT(DISTINCT Платформа) as count
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            total_df = pd.read_sql(total_platforms_query, self.conn, params=[artist_name])
            total_platforms = int(total_df['count'].iloc[0]) if not total_df.empty else 0
            
            return {
                "artist": artist_name,
                "period": period,
                "total_platforms": total_platforms,
                "top_platforms": platforms
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_geography(self, artist_name: str, period: str = "all", top_n: int = 15) -> Dict[str, Any]:
        """
        Получить географическую статистику артиста (SQLite версия)
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ стран
            
        Returns:
            Словарь с географической статистикой
        """
        try:
            sql_query = """
                SELECT 
                    "страна / регион" as country,
                    SUM(Количество) as streams,
                    SUM("Сумма вознаграждения") as revenue
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            params = [artist_name]
            
            # Фильтр по периоду
            if period == "q3_2025":
                sql_query += " AND year = 2025 AND quarter = 3"
            elif period == "q4_2025":
                sql_query += " AND year = 2025 AND quarter = 4"
            
            sql_query += f"""
                GROUP BY "страна / регион"
                ORDER BY revenue DESC
                LIMIT {top_n}
            """
            
            df = pd.read_sql(sql_query, self.conn, params=params)
            
            if df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            total_revenue = df['revenue'].sum()
            
            countries = []
            for _, row in df.iterrows():
                countries.append({
                    "country": row['country'],
                    "streams": int(row['streams']),
                    "revenue": float(row['revenue']),
                    "percentage": round((row['revenue'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            # Получаем общее количество стран
            total_countries_query = """
                SELECT COUNT(DISTINCT "страна / регион") as count
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            total_df = pd.read_sql(total_countries_query, self.conn, params=[artist_name])
            total_countries = int(total_df['count'].iloc[0]) if not total_df.empty else 0
            
            return {
                "artist": artist_name,
                "period": period,
                "total_countries": total_countries,
                "top_countries": countries
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_tracks(self, artist_name: str, period: str = "all", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить статистику по трекам артиста (SQLite версия)
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ треков
            
        Returns:
            Словарь со статистикой по трекам
        """
        try:
            sql_query = """
                SELECT 
                    "Название трека" as track_name,
                    SUM(Количество) as streams,
                    SUM("Сумма вознаграждения") as revenue
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            params = [artist_name]
            
            # Фильтр по периоду
            if period == "q3_2025":
                sql_query += " AND year = 2025 AND quarter = 3"
            elif period == "q4_2025":
                sql_query += " AND year = 2025 AND quarter = 4"
            
            sql_query += f"""
                GROUP BY "Название трека"
                ORDER BY revenue DESC
                LIMIT {top_n}
            """
            
            df = pd.read_sql(sql_query, self.conn, params=params)
            
            if df.empty:
                return {"error": f"Артист '{artist_name}' не найден"}
            
            total_revenue = df['revenue'].sum()
            
            tracks = []
            for _, row in df.iterrows():
                tracks.append({
                    "track_name": row['track_name'],
                    "streams": int(row['streams']),
                    "revenue": float(row['revenue']),
                    "percentage": round((row['revenue'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                })
            
            # Получаем общее количество треков
            total_tracks_query = """
                SELECT COUNT(DISTINCT "Название трека") as count
                FROM analytics
                WHERE LOWER(Исполнитель) = LOWER(?)
            """
            total_df = pd.read_sql(total_tracks_query, self.conn, params=[artist_name])
            total_tracks = int(total_df['count'].iloc[0]) if not total_df.empty else 0
            
            return {
                "artist": artist_name,
                "period": period,
                "total_tracks": total_tracks,
                "top_tracks": tracks
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_artist_full_analytics(self, artist_name: str, period: str = "all", top_n: int = 10) -> Dict[str, Any]:
        """
        Получить полную аналитику по артисту (SQLite версия)
        
        Args:
            artist_name: Имя артиста
            period: Период данных
            top_n: Количество топ элементов
            
        Returns:
            Словарь с полной аналитикой
        """
        try:
            # Просто вызываем отдельные методы и собираем результаты
            streams_data = self.get_artist_streams(artist_name, period)
            if "error" in streams_data:
                return streams_data
            
            platforms_data = self.get_artist_platforms(artist_name, period, top_n)
            countries_data = self.get_artist_geography(artist_name, period, top_n)
            tracks_data = self.get_artist_tracks(artist_name, period, top_n)
            
            return {
                "artist_name": artist_name,
                "period": period,
                "total_streams": streams_data["total_streams"],
                "total_revenue": streams_data["total_revenue"],
                "total_tracks": tracks_data.get("total_tracks", 0),
                "currency": "EUR",
                "top_platforms": platforms_data.get("top_platforms", []),
                "top_countries": countries_data.get("top_countries", []),
                "top_tracks": tracks_data.get("top_tracks", [])
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

