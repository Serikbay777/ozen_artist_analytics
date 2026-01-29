#!/usr/bin/env python3
"""
Скрипт для анализа топ-100 артистов за Q3 2025
с расчетом процента от общего бюджета
"""

import pandas as pd
from pathlib import Path
import json


class TopArtistsQ3Analyzer:
    """Анализатор топ артистов за Q3 2025"""
    
    def __init__(self, data_dir: str = 'data/processed'):
        """
        Инициализация анализатора
        
        Args:
            data_dir: Путь к директории с CSV файлами
        """
        self.data_dir = Path(data_dir)
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
    
    def get_quarter_from_date(self, date_str: str) -> str:
        """
        Определение квартала из даты
        
        Args:
            date_str: Строка с датой в формате "YYYY/MM/DD"
            
        Returns:
            Строка вида "Q3 2025" или "Unknown"
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
            
            # Определяем квартал
            quarter = (date_obj.month - 1) // 3 + 1
            year = date_obj.year
            
            return f"Q{quarter} {year}"
        except:
            return 'Unknown'
    
    def analyze_q3_artists(self) -> dict:
        """
        Анализ артистов за Q3 2025
        
        Returns:
            Словарь с результатами анализа
        """
        # Загружаем файл Q3 (июль-сентябрь)
        q3_file = self.data_dir / '1740260_704133_2025-07-01_2025-09-01.csv'
        
        if not q3_file.exists():
            print(f"❌ Файл не найден: {q3_file}")
            return {}
        
        print(f"📂 Загрузка данных Q3 2025...")
        print(f"   Файл: {q3_file.name}")
        
        df = pd.read_csv(
            q3_file,
            sep=';',
            encoding='utf-8',
            quotechar='"',
            low_memory=False
        )
        
        print(f"   ✓ Загружено {len(df):,} строк")
        
        # Определяем названия колонок
        artist_col = 'Исполнитель' if 'Исполнитель' in df.columns else 'Artist'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        total_revenue_col = 'Общий доход' if 'Общий доход' in df.columns else 'Total Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
        
        # Очищаем числовые колонки
        print("🧹 Очистка данных...")
        df['revenue_clean'] = self.clean_numeric_column(df, revenue_col)
        df['total_revenue_clean'] = self.clean_numeric_column(df, total_revenue_col)
        df['quantity_clean'] = self.clean_numeric_column(df, quantity_col)
        
        # Общий бюджет Q3
        total_budget = df['revenue_clean'].sum()
        
        print(f"\n💰 Общий бюджет Q3 2025: {total_budget:,.2f} EUR")
        
        # Группируем по артистам
        print("📊 Анализ артистов...")
        
        artist_stats = df.groupby(artist_col).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum',
            track_col: 'nunique'  # Количество уникальных треков
        }).round(2)
        
        artist_stats.columns = ['Доход (EUR)', 'Общий доход (EUR)', 'Стримов', 'Треков']
        
        # Добавляем процент от общего бюджета
        artist_stats['% от бюджета'] = (artist_stats['Доход (EUR)'] / total_budget * 100).round(2)
        
        # Сортируем по доходу
        artist_stats = artist_stats.sort_values('Доход (EUR)', ascending=False)
        
        # Берем топ-100
        top_100 = artist_stats.head(100)
        
        # Рассчитываем накопительный процент
        top_100['Накопительный %'] = top_100['% от бюджета'].cumsum().round(2)
        
        # Анализ Парето
        top_20_revenue = artist_stats.head(20)['Доход (EUR)'].sum()
        top_20_percent = (top_20_revenue / total_budget * 100)
        
        top_50_revenue = artist_stats.head(50)['Доход (EUR)'].sum()
        top_50_percent = (top_50_revenue / total_budget * 100)
        
        top_100_revenue = top_100['Доход (EUR)'].sum()
        top_100_percent = (top_100_revenue / total_budget * 100)
        
        self.results = {
            'top_100': top_100,
            'total_budget': total_budget,
            'total_artists': len(artist_stats),
            'top_20_revenue': top_20_revenue,
            'top_20_percent': top_20_percent,
            'top_50_revenue': top_50_revenue,
            'top_50_percent': top_50_percent,
            'top_100_revenue': top_100_revenue,
            'top_100_percent': top_100_percent,
            'all_artists': artist_stats
        }
        
        return self.results
    
    def print_report(self) -> None:
        """Вывод отчета в консоль"""
        if not self.results:
            print("⚠️  Сначала выполните analyze_q3_artists()")
            return
        
        print("\n" + "="*80)
        print("🎵 ТОП-100 АРТИСТОВ Q3 2025 (Июль-Сентябрь)")
        print("="*80)
        
        print(f"\n📊 Общая статистика:")
        print(f"   Общий бюджет Q3: {self.results['total_budget']:,.2f} EUR")
        print(f"   Всего артистов: {self.results['total_artists']:,}")
        
        print(f"\n📈 Анализ Парето:")
        print(f"   ТОП-20 артистов: {self.results['top_20_revenue']:,.2f} EUR ({self.results['top_20_percent']:.1f}%)")
        print(f"   ТОП-50 артистов: {self.results['top_50_revenue']:,.2f} EUR ({self.results['top_50_percent']:.1f}%)")
        print(f"   ТОП-100 артистов: {self.results['top_100_revenue']:,.2f} EUR ({self.results['top_100_percent']:.1f}%)")
        
        # Топ-20
        print(f"\n\n🏆 ТОП-20 АРТИСТОВ:")
        print("="*80)
        print(f"{'#':<4} {'Артист':<30} {'Доход':>12} {'% бюджета':>10} {'Накопит %':>11} {'Треков':>8}")
        print("-"*80)
        
        for idx, (artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1):
            artist_name = str(artist)[:30]
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            tracks = int(row['Треков'])
            
            print(f"{idx:<4} {artist_name:<30} {revenue:>11,.2f} € {percent:>9.2f}% {cumulative:>10.2f}% {tracks:>8}")
        
        # Топ 21-50
        print(f"\n\n📊 АРТИСТЫ 21-50:")
        print("="*80)
        print(f"{'#':<4} {'Артист':<30} {'Доход':>12} {'% бюджета':>10} {'Накопит %':>11} {'Треков':>8}")
        print("-"*80)
        
        for idx, (artist, row) in enumerate(self.results['top_100'].iloc[20:50].iterrows(), 21):
            artist_name = str(artist)[:30]
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            tracks = int(row['Треков'])
            
            print(f"{idx:<4} {artist_name:<30} {revenue:>11,.2f} € {percent:>9.2f}% {cumulative:>10.2f}% {tracks:>8}")
        
        # Топ 51-100 (кратко)
        print(f"\n\n📋 АРТИСТЫ 51-100:")
        print("="*80)
        print(f"{'#':<4} {'Артист':<30} {'Доход':>12} {'% бюджета':>10} {'Накопит %':>11} {'Треков':>8}")
        print("-"*80)
        
        for idx, (artist, row) in enumerate(self.results['top_100'].iloc[50:100].iterrows(), 51):
            artist_name = str(artist)[:30]
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            tracks = int(row['Треков'])
            
            print(f"{idx:<4} {artist_name:<30} {revenue:>11,.2f} € {percent:>9.2f}% {cumulative:>10.2f}% {tracks:>8}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str = 'reports') -> None:
        """
        Сохранение отчета в файлы
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        if not self.results:
            print("⚠️  Сначала выполните analyze_q3_artists()")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Сохранение отчетов в {output_dir}/...")
        
        # 1. Сохраняем топ-100
        top_100_report = output_path / 'top_100_artists_q3_2025.csv'
        self.results['top_100'].to_csv(top_100_report, encoding='utf-8-sig')
        print(f"   ✓ {top_100_report.name}")
        
        # 2. Сохраняем всех артистов
        all_artists_report = output_path / 'all_artists_q3_2025.csv'
        self.results['all_artists'].to_csv(all_artists_report, encoding='utf-8-sig')
        print(f"   ✓ {all_artists_report.name}")
        
        # 3. Создаем JSON с анализом
        json_report = output_path / 'top_artists_q3_summary.json'
        
        summary = {
            'period': 'Q3 2025 (Июль-Сентябрь)',
            'total_budget': float(self.results['total_budget']),
            'total_artists': int(self.results['total_artists']),
            'pareto_analysis': {
                'top_20': {
                    'revenue': float(self.results['top_20_revenue']),
                    'percent': float(self.results['top_20_percent'])
                },
                'top_50': {
                    'revenue': float(self.results['top_50_revenue']),
                    'percent': float(self.results['top_50_percent'])
                },
                'top_100': {
                    'revenue': float(self.results['top_100_revenue']),
                    'percent': float(self.results['top_100_percent'])
                }
            },
            'top_20_artists': [
                {
                    'rank': idx,
                    'artist': artist,
                    'revenue': float(row['Доход (EUR)']),
                    'percent_of_budget': float(row['% от бюджета']),
                    'cumulative_percent': float(row['Накопительный %']),
                    'tracks': int(row['Треков']),
                    'streams': int(row['Стримов'])
                }
                for idx, (artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1)
            ]
        }
        
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"   ✓ {json_report.name}")
        
        # 4. Создаем Markdown отчет
        self.create_markdown_report(output_path)
        
        print(f"\n✅ Все отчеты сохранены в {output_dir}/")
    
    def create_markdown_report(self, output_path: Path) -> None:
        """Создание красивого Markdown отчета"""
        
        md_content = []
        md_content.append("# 🎵 ТОП-100 артистов Q3 2025\n")
        md_content.append("> **Период:** Июль - Сентябрь 2025 (Q3)\n")
        md_content.append("> **Дата отчета:** 26 января 2026\n")
        md_content.append("\n---\n")
        
        # Общая статистика
        md_content.append("\n## 📊 Общая статистика\n")
        md_content.append(f"\n- **Общий бюджет Q3:** {self.results['total_budget']:,.2f} EUR\n")
        md_content.append(f"- **Всего артистов:** {self.results['total_artists']:,}\n")
        
        # Анализ Парето
        md_content.append("\n## 📈 Анализ Парето (принцип 80/20)\n")
        md_content.append("\n| Группа | Доход (EUR) | % от бюджета |\n")
        md_content.append("|--------|-------------|---------------|\n")
        md_content.append(f"| ТОП-20 артистов | {self.results['top_20_revenue']:,.2f} | {self.results['top_20_percent']:.1f}% |\n")
        md_content.append(f"| ТОП-50 артистов | {self.results['top_50_revenue']:,.2f} | {self.results['top_50_percent']:.1f}% |\n")
        md_content.append(f"| ТОП-100 артистов | {self.results['top_100_revenue']:,.2f} | {self.results['top_100_percent']:.1f}% |\n")
        
        # Топ-20
        md_content.append("\n---\n")
        md_content.append("\n## 🏆 ТОП-20 артистов\n")
        md_content.append("\n| # | Артист | Доход (EUR) | % бюджета | Накопительный % | Треков | Стримов |\n")
        md_content.append("|---|--------|-------------|-----------|-----------------|--------|----------|\n")
        
        for idx, (artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1):
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            tracks = int(row['Треков'])
            streams = int(row['Стримов'])
            
            md_content.append(f"| {idx} | {artist} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% | {tracks} | {streams:,} |\n")
        
        # Топ 21-50
        md_content.append("\n---\n")
        md_content.append("\n## 📊 Артисты 21-50\n")
        md_content.append("\n| # | Артист | Доход (EUR) | % бюджета | Накопительный % | Треков |\n")
        md_content.append("|---|--------|-------------|-----------|-----------------|--------|\n")
        
        for idx, (artist, row) in enumerate(self.results['top_100'].iloc[20:50].iterrows(), 21):
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            tracks = int(row['Треков'])
            
            md_content.append(f"| {idx} | {artist} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% | {tracks} |\n")
        
        # Топ 51-100
        md_content.append("\n---\n")
        md_content.append("\n## 📋 Артисты 51-100\n")
        md_content.append("\n| # | Артист | Доход (EUR) | % бюджета | Накопительный % |\n")
        md_content.append("|---|--------|-------------|-----------|------------------|\n")
        
        for idx, (artist, row) in enumerate(self.results['top_100'].iloc[50:100].iterrows(), 51):
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            
            md_content.append(f"| {idx} | {artist} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% |\n")
        
        md_content.append("\n---\n")
        md_content.append("\n*Отчет сгенерирован автоматически скриптом `analyze_top_artists_q3.py`*\n")
        
        # Сохраняем
        md_file = output_path / 'TOP_100_ARTISTS_Q3_2025.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.writelines(md_content)
        
        print(f"   ✓ {md_file.name}")


def main():
    """Основная функция"""
    print("🎵 Анализатор топ-100 артистов Q3 2025")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = TopArtistsQ3Analyzer(data_dir='data/processed')
    
    # Выполняем анализ
    analyzer.analyze_q3_artists()
    
    if not analyzer.results:
        print("\n❌ Ошибка при анализе данных")
        return
    
    # Выводим отчет
    analyzer.print_report()
    
    # Сохраняем результаты
    analyzer.save_report()


if __name__ == '__main__':
    main()

