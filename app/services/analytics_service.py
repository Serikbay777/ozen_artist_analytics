"""
Analytics Service - Provides comprehensive analytics data for the frontend
Based on deep_analytics.py and strategic_analytics.py scripts
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import warnings
import os

warnings.filterwarnings('ignore')


class AnalyticsService:
    """
    Analytics Service with Singleton pattern.
    Data is loaded once and shared across all instances.
    """
    _instance = None
    _df = None
    _initialized = False
    
    def __new__(cls, data_dir: str = None):
        """Singleton pattern - only one instance with loaded data"""
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, data_dir: str = None):
        """Initialize analytics service with data directory"""
        # Only load data once
        if self._initialized:
            return
            
        if data_dir is None:
            # Default path to processed data directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, 'data', 'processed')
        
        self.data_dir = data_dir
        self._load_data()
        self._initialized = True
        print(f"✅ AnalyticsService initialized with {len(self._df):,} rows")
    
    def _load_data(self):
        """Load and prepare data from all CSV files in processed directory"""
        try:
            import glob
            
            # Find all CSV files in processed directory
            csv_files = glob.glob(os.path.join(self.data_dir, '*.csv'))
            
            if not csv_files:
                print(f"⚠️  No CSV files found in {self.data_dir}, starting with empty dataset")
                self._df = pd.DataFrame()
                return
            
            print(f"📁 Loading {len(csv_files)} CSV files from {self.data_dir}")
            
            # Required columns for compatibility
            required_cols = ['Месяц отчета', 'Исполнитель', 'Название трека', 'Платформа', 'Сумма вознаграждения', 'Количество']
            
            # Read all CSV files
            dfs = []
            for csv_file in csv_files:
                try:
                    # Try reading with different separators
                    df = None
                    for sep in [',', ';']:
                        try:
                            df = pd.read_csv(csv_file, sep=sep, low_memory=False)
                            # Check if we have required columns
                            if all(col in df.columns for col in required_cols):
                                break
                            df = None
                        except:
                            continue
                    
                    if df is not None and len(df) > 0:
                        dfs.append(df)
                        print(f"   ✓ Loaded {os.path.basename(csv_file)}: {len(df):,} rows")
                    else:
                        print(f"   ⊘ Skipped {os.path.basename(csv_file)}: incompatible format (missing required columns)")
                        
                except Exception as e:
                    print(f"   ✗ Error loading {os.path.basename(csv_file)}: {e}")
            
            if not dfs:
                raise Exception("Failed to load any compatible CSV files")
            
            # Combine all dataframes
            self._df = pd.concat(dfs, ignore_index=True)
            print(f"   📊 Total rows: {len(self._df):,}")
            
            # Convert date column
            if 'Месяц отчета' in self._df.columns:
                self._df['Месяц отчета'] = pd.to_datetime(self._df['Месяц отчета'], errors='coerce')
            
            # Prepare derived columns
            self._df['year'] = self._df['Месяц отчета'].dt.year
            self._df['month'] = self._df['Месяц отчета'].dt.month
            self._df['quarter'] = self._df['Месяц отчета'].dt.quarter
            self._df['year_month'] = self._df['Месяц отчета'].dt.to_period('M')
            self._df['release_date'] = self._df.groupby(['Исполнитель', 'Название трека'])['Месяц отчета'].transform('min')
            self._df['track_age_months'] = ((self._df['Месяц отчета'] - self._df['release_date']).dt.days / 30).round(0)
            
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    @property
    def df(self) -> pd.DataFrame:
        """Get dataframe"""
        return self._df
    
    # ============================================================================
    # OVERVIEW METRICS
    # ============================================================================
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get high-level overview statistics"""
        df = self.df
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        total_streams = int(df['Количество'].sum())
        total_artists = int(df['Исполнитель'].nunique())
        total_tracks = int(df['Название трека'].nunique())
        total_platforms = int(df['Платформа'].nunique())
        total_countries = int(df['страна / регион'].nunique())
        
        # Date range
        min_date = df['Месяц отчета'].min()
        max_date = df['Месяц отчета'].max()
        
        # Average CPM
        avg_cpm = float((total_revenue / total_streams * 1000) if total_streams > 0 else 0)
        
        return {
            "total_revenue": total_revenue,
            "total_streams": total_streams,
            "total_artists": total_artists,
            "total_tracks": total_tracks,
            "total_platforms": total_platforms,
            "total_countries": total_countries,
            "avg_cpm": avg_cpm,
            "date_range": {
                "from": min_date.isoformat() if pd.notna(min_date) else None,
                "to": max_date.isoformat() if pd.notna(max_date) else None
            },
            "currency": "EUR"
        }
    
    # ============================================================================
    # YEARLY TRENDS
    # ============================================================================
    
    def get_yearly_trends(self) -> Dict[str, Any]:
        """Get year-over-year trends"""
        df = self.df
        
        yearly = df.groupby('year').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum',
            'Исполнитель': 'nunique'
        }).reset_index()
        
        yearly.columns = ['year', 'revenue', 'streams', 'artists']
        
        # Calculate YoY growth
        yearly['revenue_growth'] = yearly['revenue'].pct_change() * 100
        yearly['streams_growth'] = yearly['streams'].pct_change() * 100
        
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
                for _, row in yearly.iterrows()
            ]
        }
    
    # ============================================================================
    # MONTHLY & QUARTERLY TRENDS
    # ============================================================================
    
    def get_monthly_trends(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get monthly trends, optionally filtered by year"""
        df = self.df
        
        if year:
            df = df[df['year'] == year]
        
        monthly = df.groupby(['year', 'month']).agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        monthly['cpm'] = (monthly['Сумма вознаграждения'] / monthly['Количество'] * 1000)
        
        return {
            "months": [
                {
                    "year": int(row['year']),
                    "month": int(row['month']),
                    "revenue": float(row['Сумма вознаграждения']),
                    "streams": int(row['Количество']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in monthly.iterrows()
            ]
        }
    
    def get_quarterly_trends(self) -> Dict[str, Any]:
        """Get quarterly trends"""
        df = self.df
        
        quarterly = df.groupby(['year', 'quarter']).agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        return {
            "quarters": [
                {
                    "year": int(row['year']),
                    "quarter": int(row['quarter']),
                    "revenue": float(row['Сумма вознаграждения']),
                    "streams": int(row['Количество'])
                }
                for _, row in quarterly.iterrows()
            ]
        }
    
    # ============================================================================
    # TOP ARTISTS
    # ============================================================================
    
    def get_top_artists(self, limit: int = 20, metric: str = 'revenue') -> Dict[str, Any]:
        """Get top artists by revenue or streams"""
        df = self.df
        
        artist_stats = df.groupby('Исполнитель').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum',
            'Название трека': 'nunique',
            'Платформа': 'nunique',
            'страна / регион': 'nunique'
        }).reset_index()
        
        artist_stats.columns = ['artist', 'revenue', 'streams', 'tracks', 'platforms', 'countries']
        artist_stats['cpm'] = (artist_stats['revenue'] / artist_stats['streams'] * 1000)
        artist_stats['revenue_per_track'] = artist_stats['revenue'] / artist_stats['tracks']
        
        # Sort by metric
        sort_column = 'revenue' if metric == 'revenue' else 'streams'
        artist_stats = artist_stats.sort_values(sort_column, ascending=False).head(limit)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        
        return {
            "artists": [
                {
                    "artist": row['artist'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / total_revenue * 100),
                    "streams": int(row['streams']),
                    "tracks": int(row['tracks']),
                    "platforms": int(row['platforms']),
                    "countries": int(row['countries']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0,
                    "revenue_per_track": float(row['revenue_per_track'])
                }
                for _, row in artist_stats.iterrows()
            ]
        }
    
    # ============================================================================
    # TOP TRACKS
    # ============================================================================
    
    def get_top_tracks(self, limit: int = 20, metric: str = 'revenue') -> Dict[str, Any]:
        """Get top tracks by revenue or streams"""
        df = self.df
        
        tracks = df.groupby(['Исполнитель', 'Название трека']).agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        tracks['cpm'] = (tracks['Сумма вознаграждения'] / tracks['Количество'] * 1000)
        
        sort_column = 'Сумма вознаграждения' if metric == 'revenue' else 'Количество'
        tracks = tracks.sort_values(sort_column, ascending=False).head(limit)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        total_streams = int(df['Количество'].sum())
        
        return {
            "tracks": [
                {
                    "artist": row['Исполнитель'],
                    "track": row['Название трека'],
                    "revenue": float(row['Сумма вознаграждения']),
                    "revenue_percentage": float(row['Сумма вознаграждения'] / total_revenue * 100),
                    "streams": int(row['Количество']),
                    "streams_percentage": float(row['Количество'] / total_streams * 100),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in tracks.iterrows()
            ]
        }
    
    # ============================================================================
    # PLATFORMS
    # ============================================================================
    
    def get_platform_stats(self, limit: int = 15) -> Dict[str, Any]:
        """Get platform statistics"""
        df = self.df
        
        platforms = df.groupby('Платформа').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        platforms['cpm'] = (platforms['Сумма вознаграждения'] / platforms['Количество'] * 1000)
        platforms = platforms.sort_values('Сумма вознаграждения', ascending=False).head(limit)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        
        return {
            "platforms": [
                {
                    "platform": row['Платформа'],
                    "revenue": float(row['Сумма вознаграждения']),
                    "revenue_percentage": float(row['Сумма вознаграждения'] / total_revenue * 100),
                    "streams": int(row['Количество']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in platforms.iterrows()
            ]
        }
    
    def get_platform_growth(self) -> Dict[str, Any]:
        """Get platform growth trends (2023 vs 2024)"""
        df = self.df
        
        platforms_yearly = df.groupby(['Платформа', 'year'])['Сумма вознаграждения'].sum().reset_index()
        platforms_pivot = platforms_yearly.pivot(index='Платформа', columns='year', values='Сумма вознаграждения').fillna(0)
        
        if 2023 in platforms_pivot.columns and 2024 in platforms_pivot.columns:
            platforms_pivot['growth'] = ((platforms_pivot[2024] - platforms_pivot[2023]) / platforms_pivot[2023] * 100).replace([np.inf, -np.inf], 0)
            platforms_pivot['abs_growth'] = platforms_pivot[2024] - platforms_pivot[2023]
            
            result = platforms_pivot.reset_index()
            result = result[result[2023] > 1000].sort_values('abs_growth', ascending=False).head(15)
            
            return {
                "platforms": [
                    {
                        "platform": row['Платформа'],
                        "revenue_2023": float(row[2023]),
                        "revenue_2024": float(row[2024]),
                        "growth_percentage": float(row['growth']),
                        "absolute_growth": float(row['abs_growth'])
                    }
                    for _, row in result.iterrows()
                ]
            }
        
        return {"platforms": []}
    
    # ============================================================================
    # GEOGRAPHY
    # ============================================================================
    
    def get_country_stats(self, limit: int = 15, sort_by: str = 'revenue') -> Dict[str, Any]:
        """Get country statistics"""
        df = self.df
        
        countries = df.groupby('страна / регион').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        countries['cpm'] = (countries['Сумма вознаграждения'] / countries['Количество'] * 1000)
        
        sort_column = 'Сумма вознаграждения' if sort_by == 'revenue' else 'cpm'
        countries = countries.sort_values(sort_column, ascending=False).head(limit)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        total_streams = int(df['Количество'].sum())
        
        return {
            "countries": [
                {
                    "country": row['страна / регион'],
                    "revenue": float(row['Сумма вознаграждения']),
                    "revenue_percentage": float(row['Сумма вознаграждения'] / total_revenue * 100),
                    "streams": int(row['Количество']),
                    "streams_percentage": float(row['Количество'] / total_streams * 100),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in countries.iterrows()
            ]
        }
    
    # ============================================================================
    # REVENUE CONCENTRATION
    # ============================================================================
    
    def get_revenue_concentration(self) -> Dict[str, Any]:
        """Get revenue concentration by artists and tracks"""
        df = self.df
        total_revenue = float(df['Сумма вознаграждения'].sum())
        
        # Artists concentration
        artist_revenue = df.groupby('Исполнитель')['Сумма вознаграждения'].sum().sort_values(ascending=False)
        
        top_10_artists = float(artist_revenue.head(10).sum())
        top_20_artists = float(artist_revenue.head(20).sum())
        top_50_artists = float(artist_revenue.head(50).sum())
        
        # Tracks concentration
        track_revenue = df.groupby(['Исполнитель', 'Название трека'])['Сумма вознаграждения'].sum().sort_values(ascending=False)
        
        top_10_tracks = float(track_revenue.head(10).sum())
        top_50_tracks = float(track_revenue.head(50).sum())
        top_100_tracks = float(track_revenue.head(100).sum())
        
        return {
            "artists": {
                "top_10": {
                    "revenue": top_10_artists,
                    "percentage": top_10_artists / total_revenue * 100
                },
                "top_20": {
                    "revenue": top_20_artists,
                    "percentage": top_20_artists / total_revenue * 100
                },
                "top_50": {
                    "revenue": top_50_artists,
                    "percentage": top_50_artists / total_revenue * 100
                },
                "total_artists": int(df['Исполнитель'].nunique())
            },
            "tracks": {
                "top_10": {
                    "revenue": top_10_tracks,
                    "percentage": top_10_tracks / total_revenue * 100
                },
                "top_50": {
                    "revenue": top_50_tracks,
                    "percentage": top_50_tracks / total_revenue * 100
                },
                "top_100": {
                    "revenue": top_100_tracks,
                    "percentage": top_100_tracks / total_revenue * 100
                },
                "total_tracks": int(df['Название трека'].nunique())
            }
        }
    
    # ============================================================================
    # ARTIST GROWTH MATRIX
    # ============================================================================
    
    def get_artist_growth_matrix(self, limit: int = 20) -> Dict[str, Any]:
        """Get artist growth matrix (2023 vs 2024)"""
        df = self.df
        
        artists_2023 = df[df['year'] == 2023].groupby('Исполнитель').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        artists_2023.columns = ['artist', 'revenue_2023', 'streams_2023']
        
        artists_2024 = df[df['year'] == 2024].groupby('Исполнитель').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        artists_2024.columns = ['artist', 'revenue_2024', 'streams_2024']
        
        growth_matrix = pd.merge(artists_2023, artists_2024, on='artist', how='outer').fillna(0)
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
    
    # ============================================================================
    # TRACK LIFECYCLE
    # ============================================================================
    
    def get_track_lifecycle(self, limit: int = 15) -> Dict[str, Any]:
        """Get track lifecycle analysis"""
        df = self.df
        
        track_lifecycle = df.groupby(['Исполнитель', 'Название трека']).agg({
            'year_month': ['min', 'max', 'nunique'],
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        track_lifecycle.columns = ['artist', 'track', 'first_month', 'last_month', 'active_months', 'revenue', 'streams']
        track_lifecycle['revenue_per_month'] = track_lifecycle['revenue'] / track_lifecycle['active_months']
        
        # Long-running tracks
        long_tracks = track_lifecycle[track_lifecycle['revenue'] > 1000].sort_values('active_months', ascending=False).head(limit)
        
        # Most profitable per month
        profitable_tracks = track_lifecycle[track_lifecycle['active_months'] >= 3].sort_values('revenue_per_month', ascending=False).head(limit)
        
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
        df = self.df
        
        labels = df.groupby('Лейбл').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum',
            'Исполнитель': 'nunique',
            'Название трека': 'nunique'
        }).reset_index()
        
        labels.columns = ['label', 'revenue', 'streams', 'artists', 'tracks']
        labels['cpm'] = (labels['revenue'] / labels['streams'] * 1000)
        labels['revenue_per_artist'] = labels['revenue'] / labels['artists']
        labels = labels.sort_values('revenue', ascending=False).head(limit)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        
        return {
            "labels": [
                {
                    "label": row['label'],
                    "revenue": float(row['revenue']),
                    "revenue_percentage": float(row['revenue'] / total_revenue * 100),
                    "streams": int(row['streams']),
                    "artists": int(row['artists']),
                    "tracks": int(row['tracks']),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0,
                    "revenue_per_artist": float(row['revenue_per_artist'])
                }
                for _, row in labels.iterrows()
            ]
        }
    
    # ============================================================================
    # SALE TYPES
    # ============================================================================
    
    def get_sale_type_stats(self) -> Dict[str, Any]:
        """Get sale type statistics"""
        df = self.df
        
        sale_types = df.groupby('Тип продажи').agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        sale_types['cpm'] = (sale_types['Сумма вознаграждения'] / sale_types['Количество'] * 1000)
        
        total_revenue = float(df['Сумма вознаграждения'].sum())
        total_streams = int(df['Количество'].sum())
        
        return {
            "sale_types": [
                {
                    "type": row['Тип продажи'],
                    "revenue": float(row['Сумма вознаграждения']),
                    "revenue_percentage": float(row['Сумма вознаграждения'] / total_revenue * 100),
                    "streams": int(row['Количество']),
                    "streams_percentage": float(row['Количество'] / total_streams * 100),
                    "cpm": float(row['cpm']) if pd.notna(row['cpm']) else 0
                }
                for _, row in sale_types.iterrows()
            ]
        }
    
    # ============================================================================
    # ARTIST DIVERSITY
    # ============================================================================
    
    def get_artist_diversity(self, limit: int = 20) -> Dict[str, Any]:
        """Get artist diversification metrics"""
        df = self.df
        
        artist_diversity = df.groupby('Исполнитель').agg({
            'Платформа': 'nunique',
            'страна / регион': 'nunique',
            'Название трека': 'nunique',
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        artist_diversity.columns = ['artist', 'platforms', 'countries', 'tracks', 'revenue', 'streams']
        artist_diversity = artist_diversity.sort_values('revenue', ascending=False).head(limit)
        
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
                for _, row in artist_diversity.iterrows()
            ]
        }
    
    # ============================================================================
    # COUNTRY × PLATFORM CPM
    # ============================================================================
    
    def get_country_platform_cpm(self, limit: int = 20) -> Dict[str, Any]:
        """Get CPM by country and platform combination"""
        df = self.df
        
        # Top countries and platforms
        top_countries = df.groupby('страна / регион')['Сумма вознаграждения'].sum().nlargest(10).index
        top_platforms = df.groupby('Платформа')['Сумма вознаграждения'].sum().nlargest(10).index
        
        country_platform_cpm = df[
            (df['страна / регион'].isin(top_countries)) & 
            (df['Платформа'].isin(top_platforms))
        ].groupby(['страна / регион', 'Платформа']).agg({
            'Сумма вознаграждения': 'sum',
            'Количество': 'sum'
        }).reset_index()
        
        country_platform_cpm['cpm'] = (country_platform_cpm['Сумма вознаграждения'] / country_platform_cpm['Количество'] * 1000)
        country_platform_cpm = country_platform_cpm[country_platform_cpm['Количество'] > 10000]
        country_platform_cpm = country_platform_cpm.sort_values('cpm', ascending=False).head(limit)
        
        return {
            "combinations": [
                {
                    "country": row['страна / регион'],
                    "platform": row['Платформа'],
                    "cpm": float(row['cpm']),
                    "revenue": float(row['Сумма вознаграждения']),
                    "streams": int(row['Количество'])
                }
                for _, row in country_platform_cpm.iterrows()
            ]
        }

