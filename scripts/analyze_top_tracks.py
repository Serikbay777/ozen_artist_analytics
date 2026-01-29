#!/usr/bin/env python3
"""
Скрипт для анализа самых прибыльных треков по месяцам
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import json


class TopTracksAnalyzer:
    """Анализатор топ треков по месяцам"""
    
    def __init__(self, data_dir: str = 'data/processed'):
        """
        Инициализация анализатора
        
        Args:
            data_dir: Путь к директории с CSV файлами
        """
        self.data_dir = Path(data_dir)
        self.dataframes: List[pd.DataFrame] = []
        self.results: Dict = {}
        
    def load_csv_files(self, pattern: str = '*_*_*.csv') -> None:
        """
        Загрузка CSV файлов из директории
        
        Args:
            pattern: Паттерн для поиска файлов
        """
        csv_files = list(self.data_dir.glob(pattern))
        
        # Фильтруем файлы с числами в названиях
        csv_files = [f for f in csv_files if f.name[0].isdigit()]
        
        print(f"Найдено {len(csv_files)} CSV файлов для анализа:")
        
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
            try:
                # Читаем CSV с разделителем ";"
                df = pd.read_csv(
                    csv_file,
                    sep=';',
                    encoding='utf-8',
                    quotechar='"',
                    low_memory=False
                )
                
                # Добавляем информацию об источнике
                df['source_file'] = csv_file.name
                
                self.dataframes.append(df)
                print(f"    ✓ Загружено {len(df):,} строк")
                
            except Exception as e:
                print(f"    ✗ Ошибка при загрузке: {e}")
    
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
    
    def get_month_from_date(self, date_str: str) -> str:
        """
        Определение месяца из даты
        
        Args:
            date_str: Строка с датой в формате "YYYY/MM/DD"
            
        Returns:
            Строка вида "2025-07" или "Unknown"
        """
        try:
            if pd.isna(date_str):
                return 'Unknown'
            
            # Убираем кавычки и пробелы
            date_str = str(date_str).strip().strip('"')
            
            # Парсим дату
            date_obj = pd.to_datetime(date_str, format='%Y/%m/%d', errors='coerce')
            
            if pd.isna(date_obj):
                return 'Unknown'
            
            return date_obj.strftime('%Y-%m')
        except:
            return 'Unknown'
    
    def analyze_top_tracks(self) -> Dict:
        """
        Анализ топ треков по месяцам
        
        Returns:
            Словарь с результатами анализа
        """
        if not self.dataframes:
            print("⚠️  Нет загруженных данных для анализа")
            return {}
        
        # Объединяем все DataFrame
        print("\n📊 Объединение данных...")
        combined_df = pd.concat(self.dataframes, ignore_index=True)
        print(f"Всего строк: {len(combined_df):,}")
        
        # Определяем названия колонок
        report_month_col = 'Месяц отчета' if 'Месяц отчета' in combined_df.columns else 'Report Month'
        artist_col = 'Исполнитель' if 'Исполнитель' in combined_df.columns else 'Artist'
        track_col = 'Название трека' if 'Название трека' in combined_df.columns else 'Track Name'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in combined_df.columns else 'Revenue'
        quantity_col = 'Количество' if 'Количество' in combined_df.columns else 'Quantity'
        platform_col = 'Платформа' if 'Платформа' in combined_df.columns else 'Platform'
        
        # Очищаем числовые колонки
        print("🧹 Очистка данных...")
        combined_df['revenue_clean'] = self.clean_numeric_column(combined_df, revenue_col)
        combined_df['quantity_clean'] = self.clean_numeric_column(combined_df, quantity_col)
        
        # Определяем месяц
        print("📅 Определение месяцев...")
        combined_df['month'] = combined_df[report_month_col].apply(self.get_month_from_date)
        
        # Создаем ключ трек-исполнитель
        combined_df['track_artist'] = combined_df[artist_col].astype(str) + ' - ' + combined_df[track_col].astype(str)
        
        # Анализ по месяцам
        print("\n💰 Анализ топ треков по месяцам...")
        
        monthly_top_tracks = {}
        
        # Получаем уникальные месяцы
        months = sorted([m for m in combined_df['month'].unique() if m != 'Unknown'])
        
        for month in months:
            month_data = combined_df[combined_df['month'] == month]
            
            # Группируем по треку и исполнителю
            track_stats = month_data.groupby(['track_artist', artist_col, track_col]).agg({
                'revenue_clean': 'sum',
                'quantity_clean': 'sum',
                platform_col: lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'  # Топ платформа
            }).round(2)
            
            track_stats.columns = ['Доход (EUR)', 'Стримов', 'Топ платформа']
            track_stats = track_stats.sort_values('Доход (EUR)', ascending=False)
            
            # Берем топ-10
            top_10 = track_stats.head(10)
            
            monthly_top_tracks[month] = top_10
        
        # Общий топ треков за весь период
        print("🏆 Расчет общего топа треков...")
        
        overall_track_stats = combined_df.groupby(['track_artist', artist_col, track_col]).agg({
            'revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        
        overall_track_stats.columns = ['Доход (EUR)', 'Стримов']
        overall_track_stats = overall_track_stats.sort_values('Доход (EUR)', ascending=False)
        
        self.results = {
            'monthly_top_tracks': monthly_top_tracks,
            'overall_top_tracks': overall_track_stats.head(20),
            'total_rows': len(combined_df),
            'combined_df': combined_df
        }
        
        return self.results
    
    def print_report(self) -> None:
        """Вывод отчета в консоль"""
        if not self.results:
            print("⚠️  Сначала выполните analyze_top_tracks()")
            return
        
        print("\n" + "="*80)
        print("🎵 ТОП ТРЕКОВ ПО МЕСЯЦАМ")
        print("="*80)
        
        month_names = {
            '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
            '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
            '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
        }
        
        for month, tracks in self.results['monthly_top_tracks'].items():
            try:
                year, month_num = month.split('-')
                month_display = f"{month_names.get(month_num, month_num)} {year}"
            except:
                month_display = month
            
            print(f"\n\n📅 {month_display}")
            print("="*80)
            print(f"{'#':<4} {'Исполнитель - Трек':<50} {'Доход':>12} {'Стримов':>12}")
            print("-"*80)
            
            for idx, (track_artist, row) in enumerate(tracks.iterrows(), 1):
                artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
                track = row.name[2] if isinstance(row.name, tuple) else track_artist
                
                # Обрезаем длинные названия
                display_name = f"{artist} - {track}"
                if len(display_name) > 50:
                    display_name = display_name[:47] + "..."
                
                revenue = row['Доход (EUR)']
                streams = int(row['Стримов'])
                
                print(f"{idx:<4} {display_name:<50} {revenue:>11,.2f} € {streams:>12,}")
        
        # Общий топ
        print("\n\n" + "="*80)
        print("🏆 ТОП-20 ТРЕКОВ ЗА ВЕСЬ ПЕРИОД (Июль-Ноябрь 2025)")
        print("="*80)
        print(f"{'#':<4} {'Исполнитель - Трек':<50} {'Доход':>12} {'Стримов':>12}")
        print("-"*80)
        
        for idx, (track_artist, row) in enumerate(self.results['overall_top_tracks'].iterrows(), 1):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            
            display_name = f"{artist} - {track}"
            if len(display_name) > 50:
                display_name = display_name[:47] + "..."
            
            revenue = row['Доход (EUR)']
            streams = int(row['Стримов'])
            
            print(f"{idx:<4} {display_name:<50} {revenue:>11,.2f} € {streams:>12,}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str = 'reports') -> None:
        """
        Сохранение отчета в файлы
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        if not self.results:
            print("⚠️  Сначала выполните analyze_top_tracks()")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Сохранение отчетов в {output_dir}/...")
        
        # 1. Сохраняем общий топ треков
        overall_report = output_path / 'top_tracks_overall.csv'
        self.results['overall_top_tracks'].to_csv(overall_report, encoding='utf-8-sig')
        print(f"   ✓ {overall_report.name}")
        
        # 2. Сохраняем топ треков по месяцам
        for month, tracks in self.results['monthly_top_tracks'].items():
            month_report = output_path / f'top_tracks_{month}.csv'
            tracks.to_csv(month_report, encoding='utf-8-sig')
            print(f"   ✓ {month_report.name}")
        
        # 3. Создаем Markdown отчет
        self.create_markdown_report(output_path)
        
        print(f"\n✅ Все отчеты сохранены в {output_dir}/")
    
    def create_markdown_report(self, output_path: Path) -> None:
        """Создание красивого Markdown отчета"""
        
        month_names = {
            '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
            '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
            '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
        }
        
        md_content = []
        md_content.append("# 🎵 Топ треков по месяцам\n")
        md_content.append("> **Период анализа:** Июль - Ноябрь 2025\n")
        md_content.append("> **Дата отчета:** 26 января 2026\n")
        md_content.append("\n---\n")
        
        # Месячные топы
        for month, tracks in self.results['monthly_top_tracks'].items():
            try:
                year, month_num = month.split('-')
                month_display = f"{month_names.get(month_num, month_num)} {year}"
            except:
                month_display = month
            
            md_content.append(f"\n## 📅 {month_display}\n")
            md_content.append("\n| # | Исполнитель | Трек | Доход (EUR) | Стримов |\n")
            md_content.append("|---|-------------|------|-------------|----------|\n")
            
            for idx, (track_artist, row) in enumerate(tracks.iterrows(), 1):
                artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
                track = row.name[2] if isinstance(row.name, tuple) else track_artist
                revenue = row['Доход (EUR)']
                streams = int(row['Стримов'])
                
                md_content.append(f"| {idx} | {artist} | {track} | {revenue:,.2f} | {streams:,} |\n")
        
        # Общий топ
        md_content.append("\n---\n")
        md_content.append("\n## 🏆 ТОП-20 треков за весь период\n")
        md_content.append("\n| # | Исполнитель | Трек | Доход (EUR) | Стримов |\n")
        md_content.append("|---|-------------|------|-------------|----------|\n")
        
        for idx, (track_artist, row) in enumerate(self.results['overall_top_tracks'].iterrows(), 1):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            revenue = row['Доход (EUR)']
            streams = int(row['Стримов'])
            
            md_content.append(f"| {idx} | {artist} | {track} | {revenue:,.2f} | {streams:,} |\n")
        
        md_content.append("\n---\n")
        md_content.append("\n*Отчет сгенерирован автоматически скриптом `analyze_top_tracks.py`*\n")
        
        # Сохраняем
        md_file = output_path / 'TOP_TRACKS_ANALYSIS.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.writelines(md_content)
        
        print(f"   ✓ {md_file.name}")


def main():
    """Основная функция"""
    print("🎵 Анализатор топ треков по месяцам")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = TopTracksAnalyzer(data_dir='data/processed')
    
    # Загружаем данные
    print("\n📂 Загрузка данных...")
    analyzer.load_csv_files()
    
    if not analyzer.dataframes:
        print("\n❌ Не найдено CSV файлов для анализа")
        return
    
    # Выполняем анализ
    analyzer.analyze_top_tracks()
    
    # Выводим отчет
    analyzer.print_report()
    
    # Сохраняем результаты
    analyzer.save_report()


if __name__ == '__main__':
    main()

