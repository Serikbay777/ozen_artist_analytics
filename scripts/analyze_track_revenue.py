#!/usr/bin/env python3
"""
Скрипт для анализа доходов конкретного трека
Позволяет узнать сколько заработал трек за период
"""

import pandas as pd
from pathlib import Path
import json
import sys
from typing import Dict, List


class TrackRevenueAnalyzer:
    """Анализатор доходов конкретного трека"""
    
    def __init__(self, data_dir: str = 'data/processed', specific_file: str = None):
        """
        Инициализация анализатора
        
        Args:
            data_dir: Путь к директории с CSV файлами
            specific_file: Имя конкретного файла для анализа (опционально)
        """
        self.data_dir = Path(data_dir)
        self.specific_file = specific_file
        self.results = {}
        
    def clean_numeric_column(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Очистка и конвертация числовых колонок
        
        Args:
            df: DataFrame
            column: Название колонки
            
        Returns:
            Series с числовыми значениями
        """
        if column not in df.columns:
            return pd.Series([0] * len(df))
        
        # Заменяем запятые на точки и конвертируем в float
        return df[column].astype(str).str.replace(',', '.').astype(float)
    
    def analyze_track(self, track_name: str, artist_name: str = None) -> dict:
        """
        Анализ доходов трека
        
        Args:
            track_name: Название трека
            artist_name: Название исполнителя (опционально)
            
        Returns:
            Словарь с результатами анализа
        """
        # Загружаем CSV файлы
        if self.specific_file:
            # Если указан конкретный файл
            specific_path = self.data_dir / self.specific_file
            if specific_path.exists():
                csv_files = [specific_path]
            else:
                print(f"❌ Файл не найден: {self.specific_file}")
                return {}
        else:
            # Загружаем все CSV файлы из data/processed
            csv_files = list(self.data_dir.glob('*.csv'))
            
            # Фильтруем файлы с числами в названиях (отчеты)
            csv_files = [f for f in csv_files if f.name[0].isdigit()]
        
        if not csv_files:
            print(f"❌ Не найдено CSV файлов в {self.data_dir}")
            return {}
        
        print(f"📂 Найдено {len(csv_files)} файлов для анализа")
        print(f"🔍 Поиск трека: '{track_name}'")
        if artist_name:
            print(f"👤 Исполнитель: '{artist_name}'")
        print()
        
        all_data = []
        
        # Загружаем все файлы
        for csv_file in csv_files:
            try:
                print(f"   📄 Загрузка: {csv_file.name}...", end=" ")
                df = pd.read_csv(
                    csv_file,
                    sep=';',
                    encoding='utf-8',
                    quotechar='"',
                    low_memory=False
                )
                
                # Определяем названия колонок
                track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
                artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
                
                # Фильтруем по треку
                mask = df[track_col].astype(str).str.contains(track_name, case=False, na=False)
                
                # Если указан исполнитель, добавляем фильтр
                if artist_name:
                    mask = mask & df[artist_col].astype(str).str.contains(artist_name, case=False, na=False)
                
                filtered_df = df[mask].copy()
                
                if len(filtered_df) > 0:
                    filtered_df['source_file'] = csv_file.name
                    all_data.append(filtered_df)
                    print(f"✓ Найдено {len(filtered_df)} записей")
                else:
                    print("⊘ Не найдено записей")
                
            except Exception as e:
                print(f"✗ Ошибка: {e}")
        
        if not all_data:
            print(f"\n❌ Трек '{track_name}' не найден в данных!")
            return {}
        
        # Объединяем все данные
        print(f"\n📊 Анализ данных...")
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"   Всего записей: {len(combined_df):,}")
        
        # Определяем названия колонок
        artist_col = 'Исполнитель' if 'Исполнитель' in combined_df.columns else 'Artist'
        track_col = 'Название трека' if 'Название трека' in combined_df.columns else 'Track Name'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in combined_df.columns else 'Revenue'
        total_revenue_col = 'Общий доход' if 'Общий доход' in combined_df.columns else 'Total Revenue'
        quantity_col = 'Количество' if 'Количество' in combined_df.columns else 'Quantity'
        platform_col = 'Платформа' if 'Платформа' in combined_df.columns else 'Platform'
        country_col = 'страна / регион' if 'страна / регион' in combined_df.columns else 'Country'
        report_month_col = 'Месяц отчета' if 'Месяц отчета' in combined_df.columns else 'Report Month'
        sale_type_col = 'Тип продажи' if 'Тип продажи' in combined_df.columns else 'Sale Type'
        
        # Очищаем числовые колонки
        combined_df['revenue_clean'] = self.clean_numeric_column(combined_df, revenue_col)
        combined_df['total_revenue_clean'] = self.clean_numeric_column(combined_df, total_revenue_col)
        combined_df['quantity_clean'] = self.clean_numeric_column(combined_df, quantity_col)
        
        # Общая статистика
        total_revenue = combined_df['revenue_clean'].sum()
        total_gross_revenue = combined_df['total_revenue_clean'].sum()
        total_streams = combined_df['quantity_clean'].sum()
        
        # Находим уникальные треки (могут быть разные версии)
        unique_tracks = combined_df.groupby([artist_col, track_col]).size().reset_index(name='records')
        
        # Статистика по платформам
        platform_stats = combined_df.groupby(platform_col).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        platform_stats = platform_stats.sort_values('revenue_clean', ascending=False)
        
        # Статистика по странам
        country_stats = combined_df.groupby(country_col).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        country_stats = country_stats.sort_values('revenue_clean', ascending=False)
        
        # Статистика по месяцам отчета
        if report_month_col in combined_df.columns:
            # Преобразуем даты
            combined_df['report_month_parsed'] = pd.to_datetime(
                combined_df[report_month_col].astype(str).str.strip().str.strip('"'),
                format='%Y/%m/%d',
                errors='coerce'
            )
            combined_df['month_year'] = combined_df['report_month_parsed'].dt.strftime('%Y-%m')
            
            monthly_stats = combined_df.groupby('month_year').agg({
                'revenue_clean': 'sum',
                'total_revenue_clean': 'sum',
                'quantity_clean': 'sum'
            }).round(2)
            monthly_stats = monthly_stats.sort_index()
        else:
            monthly_stats = pd.DataFrame()
        
        # Статистика по типу продажи
        if sale_type_col in combined_df.columns:
            sale_type_stats = combined_df.groupby(sale_type_col).agg({
                'revenue_clean': 'sum',
                'quantity_clean': 'sum'
            }).round(2)
            sale_type_stats = sale_type_stats.sort_values('revenue_clean', ascending=False)
        else:
            sale_type_stats = pd.DataFrame()
        
        self.results = {
            'track_name': track_name,
            'artist_name': artist_name,
            'total_revenue': total_revenue,
            'total_gross_revenue': total_gross_revenue,
            'total_streams': total_streams,
            'total_records': len(combined_df),
            'unique_tracks': unique_tracks,
            'platform_stats': platform_stats,
            'country_stats': country_stats,
            'monthly_stats': monthly_stats,
            'sale_type_stats': sale_type_stats,
            'combined_df': combined_df
        }
        
        return self.results
    
    def print_report(self) -> None:
        """Вывод отчета в консоль"""
        if not self.results:
            print("⚠️  Сначала выполните analyze_track()")
            return
        
        print("\n" + "="*80)
        print(f"🎵 ОТЧЕТ ПО ДОХОДАМ ТРЕКА")
        print("="*80)
        
        # Основная информация
        print(f"\n📌 Трек: {self.results['track_name']}")
        if self.results['artist_name']:
            print(f"👤 Исполнитель: {self.results['artist_name']}")
        
        # Найденные треки (если есть несколько версий)
        if len(self.results['unique_tracks']) > 1:
            print(f"\n⚠️  Найдено несколько версий трека:")
            for idx, row in self.results['unique_tracks'].iterrows():
                artist = row[0]
                track = row[1]
                records = row[2]
                print(f"   - {artist} - {track} ({records} записей)")
        else:
            first_track = self.results['unique_tracks'].iloc[0]
            artist_name = first_track.iloc[0]
            track_name = first_track.iloc[1]
            print(f"   Полное название: {artist_name} - {track_name}")
        
        # Общая статистика
        print(f"\n💰 Общая статистика:")
        print("-"*80)
        print(f"   Чистый доход (ваше вознаграждение): {self.results['total_revenue']:>15,.2f} EUR")
        print(f"   Валовой доход (до отчислений):      {self.results['total_gross_revenue']:>15,.2f} EUR")
        print(f"   Количество стримов/продаж:          {int(self.results['total_streams']):>15,}")
        print(f"   Всего записей в отчетах:            {self.results['total_records']:>15,}")
        
        # Средняя цена за стрим
        if self.results['total_streams'] > 0:
            avg_revenue_per_stream = self.results['total_revenue'] / self.results['total_streams']
            print(f"   Средний доход за стрим:             {avg_revenue_per_stream:>15,.6f} EUR")
        
        # Статистика по месяцам
        if not self.results['monthly_stats'].empty:
            print(f"\n\n📅 ДОХОДЫ ПО МЕСЯЦАМ:")
            print("="*80)
            print(f"{'Месяц':<12} {'Доход':>15} {'Валовой доход':>18} {'Стримы':>12}")
            print("-"*80)
            
            for month, row in self.results['monthly_stats'].iterrows():
                if month != 'Unknown' and pd.notna(month):
                    revenue = row['revenue_clean']
                    gross = row['total_revenue_clean']
                    streams = int(row['quantity_clean'])
                    print(f"{month:<12} {revenue:>14,.2f} € {gross:>17,.2f} € {streams:>12,}")
        
        # Топ-10 платформ
        print(f"\n\n🏆 ТОП-10 ПЛАТФОРМ ПО ДОХОДАМ:")
        print("="*80)
        print(f"{'#':<3} {'Платформа':<35} {'Доход':>15} {'Стримы':>12}")
        print("-"*80)
        
        for idx, (platform, row) in enumerate(self.results['platform_stats'].head(10).iterrows(), 1):
            revenue = row['revenue_clean']
            streams = int(row['quantity_clean'])
            platform_name = platform[:34]
            print(f"{idx:<3} {platform_name:<35} {revenue:>14,.2f} € {streams:>12,}")
        
        # Топ-10 стран
        print(f"\n\n🌍 ТОП-10 СТРАН ПО ДОХОДАМ:")
        print("="*80)
        print(f"{'#':<3} {'Страна':<35} {'Доход':>15} {'Стримы':>12}")
        print("-"*80)
        
        for idx, (country, row) in enumerate(self.results['country_stats'].head(10).iterrows(), 1):
            revenue = row['revenue_clean']
            streams = int(row['quantity_clean'])
            country_name = str(country)[:34]
            print(f"{idx:<3} {country_name:<35} {revenue:>14,.2f} € {streams:>12,}")
        
        # Статистика по типу продажи
        if not self.results['sale_type_stats'].empty:
            print(f"\n\n📊 ПО ТИПУ ПРОДАЖИ:")
            print("="*80)
            print(f"{'Тип':<30} {'Доход':>15} {'Количество':>12}")
            print("-"*80)
            
            for sale_type, row in self.results['sale_type_stats'].iterrows():
                revenue = row['revenue_clean']
                quantity = int(row['quantity_clean'])
                sale_type_name = str(sale_type)[:29]
                print(f"{sale_type_name:<30} {revenue:>14,.2f} € {quantity:>12,}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str = 'reports') -> None:
        """
        Сохранение отчета в файлы
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        if not self.results:
            print("⚠️  Сначала выполните analyze_track()")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Создаем безопасное имя файла
        safe_track_name = self.results['track_name'].replace(' ', '_').replace('/', '_')
        
        print(f"\n💾 Сохранение отчетов в {output_dir}/...")
        
        # 1. Сохраняем статистику по платформам
        platform_file = output_path / f'track_{safe_track_name}_platforms.csv'
        self.results['platform_stats'].to_csv(platform_file, encoding='utf-8-sig')
        print(f"   ✓ {platform_file.name}")
        
        # 2. Сохраняем статистику по странам
        country_file = output_path / f'track_{safe_track_name}_countries.csv'
        self.results['country_stats'].to_csv(country_file, encoding='utf-8-sig')
        print(f"   ✓ {country_file.name}")
        
        # 3. Сохраняем статистику по месяцам
        if not self.results['monthly_stats'].empty:
            monthly_file = output_path / f'track_{safe_track_name}_monthly.csv'
            self.results['monthly_stats'].to_csv(monthly_file, encoding='utf-8-sig')
            print(f"   ✓ {monthly_file.name}")
        
        # 4. Сохраняем все записи трека
        all_records_file = output_path / f'track_{safe_track_name}_all_records.csv'
        self.results['combined_df'].to_csv(all_records_file, encoding='utf-8-sig', index=False)
        print(f"   ✓ {all_records_file.name}")
        
        # 5. Создаем JSON с результатами
        json_file = output_path / f'track_{safe_track_name}_summary.json'
        
        summary = {
            'track_name': self.results['track_name'],
            'artist_name': self.results['artist_name'],
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_revenue_eur': float(self.results['total_revenue']),
            'total_gross_revenue_eur': float(self.results['total_gross_revenue']),
            'total_streams': int(self.results['total_streams']),
            'total_records': self.results['total_records'],
            'average_revenue_per_stream': float(self.results['total_revenue'] / self.results['total_streams']) if self.results['total_streams'] > 0 else 0,
            'top_10_platforms': [
                {
                    'platform': platform,
                    'revenue': float(row['revenue_clean']),
                    'streams': int(row['quantity_clean'])
                }
                for platform, row in self.results['platform_stats'].head(10).iterrows()
            ],
            'top_10_countries': [
                {
                    'country': country,
                    'revenue': float(row['revenue_clean']),
                    'streams': int(row['quantity_clean'])
                }
                for country, row in self.results['country_stats'].head(10).iterrows()
            ],
            'monthly_breakdown': {
                month: {
                    'revenue': float(row['revenue_clean']),
                    'gross_revenue': float(row['total_revenue_clean']),
                    'streams': int(row['quantity_clean'])
                }
                for month, row in self.results['monthly_stats'].iterrows()
                if month != 'Unknown' and pd.notna(month)
            } if not self.results['monthly_stats'].empty else {}
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"   ✓ {json_file.name}")
        
        print(f"\n✅ Все отчеты сохранены в {output_dir}/")


def main():
    """Основная функция"""
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("🎵 Анализатор доходов трека")
        print("="*80)
        print("\nИспользование:")
        print("  python analyze_track_revenue.py <название_трека> [исполнитель] [--file имя_файла.csv]")
        print("\nПримеры:")
        print("  python analyze_track_revenue.py Unemdeme")
        print("  python analyze_track_revenue.py Unemdeme 'XAN'")
        print("  python analyze_track_revenue.py Unemdeme --file 1740260_704133_2025-07-01_2025-09-01.csv")
        print("\n")
        return
    
    track_name = sys.argv[1]
    artist_name = None
    specific_file = None
    
    # Парсим аргументы
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--file' and i + 1 < len(sys.argv):
            specific_file = sys.argv[i + 1]
            i += 2
        else:
            artist_name = sys.argv[i]
            i += 1
    
    print("🎵 Анализатор доходов трека")
    print("="*80)
    print()
    
    # Создаем анализатор
    analyzer = TrackRevenueAnalyzer(data_dir='data/processed', specific_file=specific_file)
    
    # Выполняем анализ
    results = analyzer.analyze_track(track_name, artist_name)
    
    if not results:
        print("\n❌ Не удалось выполнить анализ")
        return
    
    # Выводим отчет
    analyzer.print_report()
    
    # Сохраняем результаты
    analyzer.save_report()


if __name__ == '__main__':
    main()

