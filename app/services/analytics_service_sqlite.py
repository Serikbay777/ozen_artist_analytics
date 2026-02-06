"""
Analytics Service - SQLite version for memory efficiency
Provides comprehensive analytics data with minimal RAM usage (~50MB instead of 1.5GB)
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import warnings
import os
import subprocess

warnings.filterwarnings('ignore')


class AnalyticsService:
    """
    Analytics Service with Singleton pattern using SQLite.
    Data is stored in SQLite database, queries return small result sets.
    RAM usage: ~50MB instead of 1.5GB
    """
    _instance = None
    _conn = None
    _initialized = False
    
    def __new__(cls, db_path: str = None):
        """Singleton pattern - only one instance with database connection"""
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """Initialize analytics service with SQLite database"""
        # Only initialize once
        if self._initialized:
            return
            
        if db_path is None:
            # Default path to database
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'analytics.db')
        
        self.db_path = db_path
        self._init_database()
        self._initialized = True
        
        # Get row count
        row_count = self._execute_query("SELECT COUNT(*) as count FROM analytics")[0]['count']
        print(f"✅ AnalyticsService initialized with {row_count:,} rows (SQLite mode)")
    
    def _init_database(self):
        """Initialize database connection and create DB if needed"""
        # Check if database exists
        if not os.path.exists(self.db_path):
            print(f"⚠️  Database not found: {self.db_path}")
            print(f"🔧 Creating database from CSV files...")
            
            # Run csv_to_sqlite.py script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script_path = os.path.join(base_dir, 'scripts', 'csv_to_sqlite.py')
            data_dir = os.path.join(base_dir, 'data', 'processed')
            
            try:
                subprocess.run([
                    'python3', script_path,
                    '--data-dir', data_dir,
                    '--db-path', self.db_path
                ], check=True)
            except Exception as e:
                raise Exception(f"Failed to create database: {e}")
        
        # Connect to database
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Optimize SQLite for read performance
        self._conn.execute('PRAGMA journal_mode=WAL')
        self._conn.execute('PRAGMA synchronous=NORMAL')
        self._conn.execute('PRAGMA cache_size=10000')
        self._conn.execute('PRAGMA temp_store=MEMORY')
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SQL query and return results as list of dicts"""
        cursor = self._conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def _query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SQL query and return pandas DataFrame"""
        return pd.read_sql_query(query, self._conn, params=params)
    
    @property
    def conn(self):
        """Get database connection"""
        return self._conn
    
    # ============================================================================
    # OVERVIEW METRICS
    # ============================================================================
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get high-level overview statistics"""
        query = """
            SELECT 
                SUM("Сумма вознаграждения") as total_revenue,
                SUM("Количество") as total_streams,
                COUNT(DISTINCT "Исполнитель") as total_artists,
                COUNT(DISTINCT "Название трека") as total_tracks,
                COUNT(DISTINCT "Платформа") as total_platforms,
                COUNT(DISTINCT "страна / регион") as total_countries,
                MIN("Месяц отчета") as min_date,
                MAX("Месяц отчета") as max_date
            FROM analytics
        """
        
        result = self._execute_query(query)[0]
        
        # Calculate average CPM
        avg_cpm = (result['total_revenue'] / result['total_streams'] * 1000) if result['total_streams'] > 0 else 0
        
        return {
            "total_revenue": float(result['total_revenue'] or 0),
            "total_streams": int(result['total_streams'] or 0),
            "total_artists": int(result['total_artists'] or 0),
            "total_tracks": int(result['total_tracks'] or 0),
            "total_platforms": int(result['total_platforms'] or 0),
            "total_countries": int(result['total_countries'] or 0),
            "avg_cpm": float(avg_cpm),
            "date_range": {
                "from": result['min_date'],
                "to": result['max_date']
            },
            "currency": "EUR"
        }
    
    # ============================================================================
    # YEARLY TRENDS
    # ============================================================================
    
    def get_yearly_trends(self) -> Dict[str, Any]:
        """Get year-over-year trends"""
        query = """
            SELECT 
                year,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams,
                COUNT(DISTINCT "Исполнитель") as artists
            FROM analytics
            GROUP BY year
            ORDER BY year
        """
        
        df = self._query_to_df(query)
        
        # Calculate YoY growth
        df['revenue_growth'] = df['revenue'].pct_change() * 100
        df['streams_growth'] = df['streams'].pct_change() * 100
        
        return {
            "years": [
                {
                    "year": int(row['year']),
                    "revenue": float(row['revenue']),
                    "streams": int(row['streams']),
                    "artists": int(row['artists']),
                    "revenue_growth": float(row['revenue_growth']) if pd.notna(row['revenue_growth']) else None,
                    "streams_growth": float(row['streams_growth']) if pd.notna(row['streams_growth']) else None
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # MONTHLY & QUARTERLY TRENDS
    # ============================================================================
    
    def get_monthly_trends(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get monthly trends, optionally filtered by year"""
        query = """
            SELECT 
                year,
                month,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            {where_clause}
            GROUP BY year, month
            ORDER BY year, month
        """
        
        where_clause = f"WHERE year = {year}" if year else ""
        query = query.format(where_clause=where_clause)
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        
        return {
            "months": [
                {
                    "year": int(row['year']),
                    "month": int(row['month']),
                    "revenue": float(row['revenue']),
                    "streams": int(row['streams']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in df.iterrows()
            ]
        }
    
    def get_quarterly_trends(self) -> Dict[str, Any]:
        """Get quarterly trends"""
        query = """
            SELECT 
                year,
                quarter,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY year, quarter
            ORDER BY year, quarter
        """
        
        df = self._query_to_df(query)
        
        return {
            "quarters": [
                {
                    "year": int(row['year']),
                    "quarter": int(row['quarter']),
                    "revenue": float(row['revenue']),
                    "streams": int(row['streams'])
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # TOP ARTISTS
    # ============================================================================
    
    def get_top_artists(self, limit: int = 20, metric: str = 'revenue') -> Dict[str, Any]:
        """Get top artists by revenue or streams"""
        sort_column = '"Сумма вознаграждения"' if metric == 'revenue' else '"Количество"'
        
        query = f"""
            SELECT 
                "Исполнитель" as artist,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams,
                COUNT(DISTINCT "Название трека") as tracks,
                COUNT(DISTINCT "Платформа") as platforms,
                COUNT(DISTINCT "страна / регион") as countries
            FROM analytics
            GROUP BY "Исполнитель"
            ORDER BY {sort_column} DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        df['revenue_per_track'] = df['revenue'] / df['tracks']
        
        # Get total revenue for percentages
        total_revenue = self._execute_query('SELECT SUM("Сумма вознаграждения") as total FROM analytics')[0]['total']
        
        return {
            "artists": [
                {
                    "artist": row['artist'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / total_revenue * 100) if total_revenue > 0 else 0,
                    "streams": int(row['streams']),
                    "tracks": int(row['tracks']),
                    "platforms": int(row['platforms']),
                    "countries": int(row['countries']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0,
                    "revenue_per_track": float(row['revenue_per_track'])
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # TOP TRACKS
    # ============================================================================
    
    def get_top_tracks(self, limit: int = 20, metric: str = 'revenue') -> Dict[str, Any]:
        """Get top tracks by revenue or streams"""
        sort_column = '"Сумма вознаграждения"' if metric == 'revenue' else '"Количество"'
        
        query = f"""
            SELECT 
                "Исполнитель" as artist,
                "Название трека" as track,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "Исполнитель", "Название трека"
            ORDER BY {sort_column} DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        
        # Get totals for percentages
        totals = self._execute_query('''
            SELECT 
                SUM("Сумма вознаграждения") as total_revenue,
                SUM("Количество") as total_streams
            FROM analytics
        ''')[0]
        
        return {
            "tracks": [
                {
                    "artist": row['artist'],
                    "track": row['track'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / totals['total_revenue'] * 100) if totals['total_revenue'] > 0 else 0,
                    "streams": int(row['streams']),
                    "streams_percentage": float(row['streams'] / totals['total_streams'] * 100) if totals['total_streams'] > 0 else 0,
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # PLATFORMS
    # ============================================================================
    
    def get_platform_stats(self, limit: int = 15) -> Dict[str, Any]:
        """Get platform statistics"""
        query = f"""
            SELECT 
                "Платформа" as platform,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "Платформа"
            ORDER BY revenue DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        
        total_revenue = self._execute_query('SELECT SUM("Сумма вознаграждения") as total FROM analytics')[0]['total']
        
        return {
            "platforms": [
                {
                    "platform": row['platform'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / total_revenue * 100) if total_revenue > 0 else 0,
                    "streams": int(row['streams']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in df.iterrows()
            ]
        }
    
    def get_platform_growth(self) -> Dict[str, Any]:
        """Get platform growth trends (2023 vs 2024)"""
        query = """
            SELECT 
                "Платформа" as platform,
                year,
                SUM("Сумма вознаграждения") as revenue
            FROM analytics
            WHERE year IN (2023, 2024)
            GROUP BY "Платформа", year
            HAVING SUM("Сумма вознаграждения") > 1000
        """
        
        df = self._query_to_df(query)
        
        # Pivot to get 2023 and 2024 columns
        pivot = df.pivot_table(index='platform', columns='year', values='revenue', fill_value=0)
        
        if 2023 in pivot.columns and 2024 in pivot.columns:
            pivot['growth'] = ((pivot[2024] - pivot[2023]) / pivot[2023] * 100).replace([np.inf, -np.inf], 0)
            pivot['abs_growth'] = pivot[2024] - pivot[2023]
            pivot = pivot.sort_values('abs_growth', ascending=False).head(15)
            
            return {
                "platforms": [
                    {
                        "platform": platform,
                        "revenue_2023": float(row[2023]),
                        "revenue_2024": float(row[2024]),
                        "growth_percentage": float(row['growth']),
                        "absolute_growth": float(row['abs_growth'])
                    }
                    for platform, row in pivot.iterrows()
                ]
            }
        
        return {"platforms": []}
    
    # ============================================================================
    # GEOGRAPHY
    # ============================================================================
    
    def get_country_stats(self, limit: int = 15, sort_by: str = 'revenue') -> Dict[str, Any]:
        """Get country statistics"""
        sort_column = 'revenue' if sort_by == 'revenue' else 'cpm'
        
        query = f"""
            SELECT 
                "страна / регион" as country,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "страна / регион"
            ORDER BY {sort_column} DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        
        if sort_by == 'cpm':
            df = df.sort_values('cpm', ascending=False).head(limit)
        
        totals = self._execute_query('''
            SELECT 
                SUM("Сумма вознаграждения") as total_revenue,
                SUM("Количество") as total_streams
            FROM analytics
        ''')[0]
        
        return {
            "countries": [
                {
                    "country": row['country'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / totals['total_revenue'] * 100) if totals['total_revenue'] > 0 else 0,
                    "streams": int(row['streams']),
                    "streams_percentage": float(row['streams'] / totals['total_streams'] * 100) if totals['total_streams'] > 0 else 0,
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in df.iterrows()
            ]
        }
    
    def get_country_platform_cpm(self, limit: int = 20) -> Dict[str, Any]:
        """Get CPM by country and platform combination"""
        query = f"""
            SELECT 
                "страна / регион" as country,
                "Платформа" as platform,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "страна / регион", "Платформа"
            HAVING SUM("Количество") > 10000
            ORDER BY revenue DESC
            LIMIT 100
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        df = df.sort_values('cpm', ascending=False).head(limit)
        
        return {
            "combinations": [
                {
                    "country": row['country'],
                    "platform": row['platform'],
                    "cpm": float(row['cpm']),
                    "revenue": float(row['revenue']),
                    "streams": int(row['streams'])
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # REVENUE CONCENTRATION
    # ============================================================================
    
    def get_revenue_concentration(self) -> Dict[str, Any]:
        """Get revenue concentration by artists and tracks"""
        total_revenue = self._execute_query('SELECT SUM("Сумма вознаграждения") as total FROM analytics')[0]['total']
        
        # Artists concentration
        artist_query = """
            SELECT SUM("Сумма вознаграждения") as revenue
            FROM (
                SELECT "Исполнитель", SUM("Сумма вознаграждения") as "Сумма вознаграждения"
                FROM analytics
                GROUP BY "Исполнитель"
                ORDER BY "Сумма вознаграждения" DESC
                LIMIT ?
            )
        """
        
        top_10_artists = self._execute_query(artist_query, (10,))[0]['revenue']
        top_20_artists = self._execute_query(artist_query, (20,))[0]['revenue']
        top_50_artists = self._execute_query(artist_query, (50,))[0]['revenue']
        
        # Tracks concentration
        track_query = """
            SELECT SUM(revenue) as revenue
            FROM (
                SELECT "Исполнитель", "Название трека", SUM("Сумма вознаграждения") as revenue
                FROM analytics
                GROUP BY "Исполнитель", "Название трека"
                ORDER BY revenue DESC
                LIMIT ?
            )
        """
        
        top_10_tracks = self._execute_query(track_query, (10,))[0]['revenue']
        top_50_tracks = self._execute_query(track_query, (50,))[0]['revenue']
        top_100_tracks = self._execute_query(track_query, (100,))[0]['revenue']
        
        # Total counts
        total_artists = self._execute_query('SELECT COUNT(DISTINCT "Исполнитель") as count FROM analytics')[0]['count']
        total_tracks = self._execute_query('SELECT COUNT(DISTINCT "Исполнитель" || "Название трека") as count FROM analytics')[0]['count']
        
        return {
            "artists": {
                "top_10": {
                    "revenue": float(top_10_artists or 0),
                    "percentage": float(top_10_artists / total_revenue * 100) if total_revenue > 0 else 0
                },
                "top_20": {
                    "revenue": float(top_20_artists or 0),
                    "percentage": float(top_20_artists / total_revenue * 100) if total_revenue > 0 else 0
                },
                "top_50": {
                    "revenue": float(top_50_artists or 0),
                    "percentage": float(top_50_artists / total_revenue * 100) if total_revenue > 0 else 0
                },
                "total_artists": int(total_artists)
            },
            "tracks": {
                "top_10": {
                    "revenue": float(top_10_tracks or 0),
                    "percentage": float(top_10_tracks / total_revenue * 100) if total_revenue > 0 else 0
                },
                "top_50": {
                    "revenue": float(top_50_tracks or 0),
                    "percentage": float(top_50_tracks / total_revenue * 100) if total_revenue > 0 else 0
                },
                "top_100": {
                    "revenue": float(top_100_tracks or 0),
                    "percentage": float(top_100_tracks / total_revenue * 100) if total_revenue > 0 else 0
                },
                "total_tracks": int(total_tracks)
            }
        }
    
    # ============================================================================
    # ARTIST GROWTH MATRIX
    # ============================================================================
    
    def get_artist_growth_matrix(self, limit: int = 20) -> Dict[str, Any]:
        """Get artist growth matrix (2023 vs 2024)"""
        query = """
            SELECT 
                "Исполнитель" as artist,
                year,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            WHERE year IN (2023, 2024)
            GROUP BY "Исполнитель", year
        """
        
        df = self._query_to_df(query)
        
        # Pivot to get 2023 and 2024 columns
        revenue_pivot = df.pivot_table(index='artist', columns='year', values='revenue', fill_value=0)
        streams_pivot = df.pivot_table(index='artist', columns='year', values='streams', fill_value=0)
        
        if 2023 in revenue_pivot.columns and 2024 in revenue_pivot.columns:
            growth_matrix = pd.DataFrame({
                'artist': revenue_pivot.index,
                'revenue_2023': revenue_pivot[2023].values,
                'revenue_2024': revenue_pivot[2024].values,
                'streams_2023': streams_pivot[2023].values,
                'streams_2024': streams_pivot[2024].values
            })
            
            growth_matrix['growth_percentage'] = ((growth_matrix['revenue_2024'] - growth_matrix['revenue_2023']) / growth_matrix['revenue_2023'] * 100).replace([np.inf, -np.inf], 0)
            growth_matrix['absolute_growth'] = growth_matrix['revenue_2024'] - growth_matrix['revenue_2023']
            
            # Categorize artists
            def categorize_artist(row):
                rev_2023 = row['revenue_2023']
                rev_2024 = row['revenue_2024']
                growth = row['growth_percentage']
                
                if rev_2023 == 0 and rev_2024 > 1000:
                    return 'new_star'
                elif rev_2024 > 10000 and growth > 50:
                    return 'rising_star'
                elif rev_2024 > 10000 and growth > 0:
                    return 'stable_star'
                elif rev_2024 > 5000 and growth > 100:
                    return 'breakthrough'
                elif rev_2024 > 1000 and growth > 0:
                    return 'growing'
                elif rev_2024 > 1000 and growth < 0:
                    return 'declining'
                else:
                    return 'emerging'
            
            growth_matrix['category'] = growth_matrix.apply(categorize_artist, axis=1)
            
            # Get top by category
            categories = {}
            for category in ['new_star', 'rising_star', 'stable_star', 'breakthrough']:
                cat_data = growth_matrix[growth_matrix['category'] == category].sort_values('revenue_2024', ascending=False).head(limit)
                categories[category] = [
                    {
                        "artist": row['artist'],
                        "revenue_2023": float(row['revenue_2023']),
                        "revenue_2024": float(row['revenue_2024']),
                        "growth_percentage": float(row['growth_percentage']),
                        "absolute_growth": float(row['absolute_growth']),
                        "streams_2023": int(row['streams_2023']),
                        "streams_2024": int(row['streams_2024'])
                    }
                    for _, row in cat_data.iterrows()
                ]
            
            # Category summary
            category_summary = growth_matrix.groupby('category').agg({
                'artist': 'count',
                'revenue_2024': 'sum'
            }).reset_index()
            
            return {
                "categories": categories,
                "summary": [
                    {
                        "category": row['category'],
                        "count": int(row['artist']),
                        "total_revenue_2024": float(row['revenue_2024'])
                    }
                    for _, row in category_summary.iterrows()
                ]
            }
        
        return {"categories": {}, "summary": []}
    
    # ============================================================================
    # TRACK LIFECYCLE
    # ============================================================================
    
    def get_track_lifecycle(self, limit: int = 15) -> Dict[str, Any]:
        """Get track lifecycle analysis"""
        query = """
            SELECT 
                "Исполнитель" as artist,
                "Название трека" as track,
                MIN("Месяц отчета") as first_month,
                MAX("Месяц отчета") as last_month,
                COUNT(DISTINCT strftime('%Y-%m', "Месяц отчета")) as active_months,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "Исполнитель", "Название трека"
            HAVING revenue > 1000
        """
        
        df = self._query_to_df(query)
        df['revenue_per_month'] = df['revenue'] / df['active_months']
        
        # Long-running tracks
        long_tracks = df.sort_values('active_months', ascending=False).head(limit)
        
        # Most profitable per month
        profitable_tracks = df[df['active_months'] >= 3].sort_values('revenue_per_month', ascending=False).head(limit)
        
        return {
            "long_running": [
                {
                    "artist": row['artist'],
                    "track": row['track'],
                    "active_months": int(row['active_months']),
                    "revenue": float(row['revenue']),
                    "revenue_per_month": float(row['revenue_per_month']),
                    "streams": int(row['streams'])
                }
                for _, row in long_tracks.iterrows()
            ],
            "most_profitable_per_month": [
                {
                    "artist": row['artist'],
                    "track": row['track'],
                    "active_months": int(row['active_months']),
                    "revenue": float(row['revenue']),
                    "revenue_per_month": float(row['revenue_per_month']),
                    "streams": int(row['streams'])
                }
                for _, row in profitable_tracks.iterrows()
            ]
        }
    
    # ============================================================================
    # LABELS
    # ============================================================================
    
    def get_label_stats(self, limit: int = 10) -> Dict[str, Any]:
        """Get label statistics"""
        query = f"""
            SELECT 
                "Лейбл" as label,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams,
                COUNT(DISTINCT "Исполнитель") as artists,
                COUNT(DISTINCT "Название трека") as tracks
            FROM analytics
            GROUP BY "Лейбл"
            ORDER BY revenue DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        df['revenue_per_artist'] = df['revenue'] / df['artists']
        
        total_revenue = self._execute_query('SELECT SUM("Сумма вознаграждения") as total FROM analytics')[0]['total']
        
        return {
            "labels": [
                {
                    "label": row['label'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / total_revenue * 100) if total_revenue > 0 else 0,
                    "streams": int(row['streams']),
                    "artists": int(row['artists']),
                    "tracks": int(row['tracks']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0,
                    "revenue_per_artist": float(row['revenue_per_artist'])
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # SALE TYPES
    # ============================================================================
    
    def get_sale_type_stats(self) -> Dict[str, Any]:
        """Get sale type statistics"""
        query = """
            SELECT 
                "Тип продажи" as type,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "Тип продажи"
            ORDER BY revenue DESC
        """
        
        df = self._query_to_df(query)
        df['cpm'] = (df['revenue'] / df['streams'] * 1000)
        
        totals = self._execute_query('''
            SELECT 
                SUM("Сумма вознаграждения") as total_revenue,
                SUM("Количество") as total_streams
            FROM analytics
        ''')[0]
        
        return {
            "sale_types": [
                {
                    "type": row['type'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / totals['total_revenue'] * 100) if totals['total_revenue'] > 0 else 0,
                    "streams": int(row['streams']),
                    "streams_percentage": float(row['streams'] / totals['total_streams'] * 100) if totals['total_streams'] > 0 else 0,
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # ARTIST DIVERSITY
    # ============================================================================
    
    def get_artist_diversity(self, limit: int = 20) -> Dict[str, Any]:
        """Get artist diversification metrics"""
        query = f"""
            SELECT 
                "Исполнитель" as artist,
                COUNT(DISTINCT "Платформа") as platforms,
                COUNT(DISTINCT "страна / регион") as countries,
                COUNT(DISTINCT "Название трека") as tracks,
                SUM("Сумма вознаграждения") as revenue,
                SUM("Количество") as streams
            FROM analytics
            GROUP BY "Исполнитель"
            ORDER BY revenue DESC
            LIMIT {limit}
        """
        
        df = self._query_to_df(query)
        
        return {
            "artists": [
                {
                    "artist": row['artist'],
                    "revenue": float(row['revenue']),
                    "streams": int(row['streams']),
                    "tracks": int(row['tracks']),
                    "platforms": int(row['platforms']),
                    "countries": int(row['countries'])
                }
                for _, row in df.iterrows()
            ]
        }
    
    # ============================================================================
    # COMPATIBILITY: df property for backward compatibility
    # ============================================================================
    
    @property
    def df(self) -> pd.DataFrame:
        """
        Backward compatibility: return full dataframe
        WARNING: This loads all data into memory! Use only when necessary.
        """
        print("⚠️  Warning: Loading full dataset into memory (compatibility mode)")
        return pd.read_sql_query("SELECT * FROM analytics", self._conn)

