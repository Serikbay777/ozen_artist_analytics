#!/usr/bin/env python3
"""
Скрипт для анализа топ-100 треков за Q3 2025
с расчетом процента от общего бюджета
"""

import pandas as pd
from pathlib import Path
import json


class TopTracksQ3Analyzer:
    """Анализатор топ треков за Q3 2025"""
    
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
    
    def analyze_q3_tracks(self) -> dict:
        """
        Анализ треков за Q3 2025
        
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
        track_col = 'Название трека' if 'Название трека' in df.columns else 'Track Name'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in df.columns else 'Revenue'
        total_revenue_col = 'Общий доход' if 'Общий доход' in df.columns else 'Total Revenue'
        quantity_col = 'Количество' if 'Количество' in df.columns else 'Quantity'
        platform_col = 'Платформа' if 'Платформа' in df.columns else 'Platform'
        
        # Очищаем числовые колонки
        print("🧹 Очистка данных...")
        df['revenue_clean'] = self.clean_numeric_column(df, revenue_col)
        df['total_revenue_clean'] = self.clean_numeric_column(df, total_revenue_col)
        df['quantity_clean'] = self.clean_numeric_column(df, quantity_col)
        
        # Общий бюджет Q3
        total_budget = df['revenue_clean'].sum()
        
        print(f"\n💰 Общий бюджет Q3 2025: {total_budget:,.2f} EUR")
        
        # Создаем ключ трек-исполнитель
        df['track_artist'] = df[artist_col].astype(str) + ' - ' + df[track_col].astype(str)
        
        # Группируем по трекам
        print("📊 Анализ треков...")
        
        track_stats = df.groupby(['track_artist', artist_col, track_col]).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum',
            platform_col: 'nunique'  # Количество платформ
        }).round(2)
        
        track_stats.columns = ['Доход (EUR)', 'Общий доход (EUR)', 'Стримов', 'Платформ']
        
        # Добавляем процент от общего бюджета
        track_stats['% от бюджета'] = (track_stats['Доход (EUR)'] / total_budget * 100).round(2)
        
        # Сортируем по доходу
        track_stats = track_stats.sort_values('Доход (EUR)', ascending=False)
        
        # Берем топ-100
        top_100 = track_stats.head(100).copy()
        
        # Рассчитываем накопительный процент
        top_100['Накопительный %'] = top_100['% от бюджета'].cumsum().round(2)
        
        # Анализ Парето
        top_20_revenue = track_stats.head(20)['Доход (EUR)'].sum()
        top_20_percent = (top_20_revenue / total_budget * 100)
        
        top_50_revenue = track_stats.head(50)['Доход (EUR)'].sum()
        top_50_percent = (top_50_revenue / total_budget * 100)
        
        top_100_revenue = top_100['Доход (EUR)'].sum()
        top_100_percent = (top_100_revenue / total_budget * 100)
        
        self.results = {
            'top_100': top_100,
            'total_budget': total_budget,
            'total_tracks': len(track_stats),
            'top_20_revenue': top_20_revenue,
            'top_20_percent': top_20_percent,
            'top_50_revenue': top_50_revenue,
            'top_50_percent': top_50_percent,
            'top_100_revenue': top_100_revenue,
            'top_100_percent': top_100_percent,
            'all_tracks': track_stats
        }
        
        return self.results
    
    def print_report(self) -> None:
        """Вывод отчета в консоль"""
        if not self.results:
            print("⚠️  Сначала выполните analyze_q3_tracks()")
            return
        
        print("\n" + "="*80)
        print("🎵 ТОП-100 ТРЕКОВ Q3 2025 (Июль-Сентябрь)")
        print("="*80)
        
        print(f"\n📊 Общая статистика:")
        print(f"   Общий бюджет Q3: {self.results['total_budget']:,.2f} EUR")
        print(f"   Всего треков: {self.results['total_tracks']:,}")
        
        print(f"\n📈 Анализ Парето:")
        print(f"   ТОП-20 треков: {self.results['top_20_revenue']:,.2f} EUR ({self.results['top_20_percent']:.1f}%)")
        print(f"   ТОП-50 треков: {self.results['top_50_revenue']:,.2f} EUR ({self.results['top_50_percent']:.1f}%)")
        print(f"   ТОП-100 треков: {self.results['top_100_revenue']:,.2f} EUR ({self.results['top_100_percent']:.1f}%)")
        
        # Топ-20
        print(f"\n\n🏆 ТОП-20 ТРЕКОВ:")
        print("="*80)
        print(f"{'#':<4} {'Исполнитель - Трек':<45} {'Доход':>12} {'% бюдж':>8} {'Накоп %':>8} {'Стримов':>10}")
        print("-"*80)
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            
            display_name = f"{artist} - {track}"
            if len(display_name) > 45:
                display_name = display_name[:42] + "..."
            
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            streams = int(row['Стримов'])
            
            print(f"{idx:<4} {display_name:<45} {revenue:>11,.2f} € {percent:>7.2f}% {cumulative:>7.2f}% {streams:>10,}")
        
        # Топ 21-50
        print(f"\n\n📊 ТРЕКИ 21-50:")
        print("="*80)
        print(f"{'#':<4} {'Исполнитель - Трек':<45} {'Доход':>12} {'% бюдж':>8} {'Накоп %':>8}")
        print("-"*80)
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].iloc[20:50].iterrows(), 21):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            
            display_name = f"{artist} - {track}"
            if len(display_name) > 45:
                display_name = display_name[:42] + "..."
            
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            
            print(f"{idx:<4} {display_name:<45} {revenue:>11,.2f} € {percent:>7.2f}% {cumulative:>7.2f}%")
        
        # Топ 51-100 (кратко)
        print(f"\n\n📋 ТРЕКИ 51-100:")
        print("="*80)
        print(f"{'#':<4} {'Исполнитель - Трек':<45} {'Доход':>12} {'% бюдж':>8} {'Накоп %':>8}")
        print("-"*80)
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].iloc[50:100].iterrows(), 51):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            
            display_name = f"{artist} - {track}"
            if len(display_name) > 45:
                display_name = display_name[:42] + "..."
            
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            
            print(f"{idx:<4} {display_name:<45} {revenue:>11,.2f} € {percent:>7.2f}% {cumulative:>7.2f}%")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str = 'reports') -> None:
        """
        Сохранение отчета в файлы
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        if not self.results:
            print("⚠️  Сначала выполните analyze_q3_tracks()")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Сохранение отчетов в {output_dir}/...")
        
        # 1. Сохраняем топ-100
        top_100_report = output_path / 'top_100_tracks_q3_2025.csv'
        self.results['top_100'].to_csv(top_100_report, encoding='utf-8-sig')
        print(f"   ✓ {top_100_report.name}")
        
        # 2. Сохраняем все треки
        all_tracks_report = output_path / 'all_tracks_q3_2025.csv'
        self.results['all_tracks'].to_csv(all_tracks_report, encoding='utf-8-sig')
        print(f"   ✓ {all_tracks_report.name}")
        
        # 3. Создаем JSON с анализом
        json_report = output_path / 'top_tracks_q3_summary.json'
        
        summary = {
            'period': 'Q3 2025 (Июль-Сентябрь)',
            'total_budget': float(self.results['total_budget']),
            'total_tracks': int(self.results['total_tracks']),
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
            'top_20_tracks': [
                {
                    'rank': idx,
                    'artist': row.name[1] if isinstance(row.name, tuple) else 'Unknown',
                    'track': row.name[2] if isinstance(row.name, tuple) else track_artist,
                    'revenue': float(row['Доход (EUR)']),
                    'percent_of_budget': float(row['% от бюджета']),
                    'cumulative_percent': float(row['Накопительный %']),
                    'streams': int(row['Стримов']),
                    'platforms': int(row['Платформ'])
                }
                for idx, (track_artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1)
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
        md_content.append("# 🎵 ТОП-100 треков Q3 2025\n")
        md_content.append("> **Период:** Июль - Сентябрь 2025 (Q3)\n")
        md_content.append("> **Дата отчета:** 26 января 2026\n")
        md_content.append("\n---\n")
        
        # Общая статистика
        md_content.append("\n## 📊 Общая статистика\n")
        md_content.append(f"\n- **Общий бюджет Q3:** {self.results['total_budget']:,.2f} EUR\n")
        md_content.append(f"- **Всего треков:** {self.results['total_tracks']:,}\n")
        
        # Анализ Парето
        md_content.append("\n## 📈 Анализ Парето (принцип 80/20)\n")
        md_content.append("\n| Группа | Доход (EUR) | % от бюджета |\n")
        md_content.append("|--------|-------------|---------------|\n")
        md_content.append(f"| ТОП-20 треков | {self.results['top_20_revenue']:,.2f} | {self.results['top_20_percent']:.1f}% |\n")
        md_content.append(f"| ТОП-50 треков | {self.results['top_50_revenue']:,.2f} | {self.results['top_50_percent']:.1f}% |\n")
        md_content.append(f"| ТОП-100 треков | {self.results['top_100_revenue']:,.2f} | {self.results['top_100_percent']:.1f}% |\n")
        
        # Топ-20
        md_content.append("\n---\n")
        md_content.append("\n## 🏆 ТОП-20 треков\n")
        md_content.append("\n| # | Исполнитель | Трек | Доход (EUR) | % бюджета | Накопительный % | Стримов |\n")
        md_content.append("|---|-------------|------|-------------|-----------|-----------------|----------|\n")
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].head(20).iterrows(), 1):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            streams = int(row['Стримов'])
            
            md_content.append(f"| {idx} | {artist} | {track} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% | {streams:,} |\n")
        
        # Топ 21-50
        md_content.append("\n---\n")
        md_content.append("\n## 📊 Треки 21-50\n")
        md_content.append("\n| # | Исполнитель | Трек | Доход (EUR) | % бюджета | Накопительный % |\n")
        md_content.append("|---|-------------|------|-------------|-----------|------------------|\n")
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].iloc[20:50].iterrows(), 21):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            
            md_content.append(f"| {idx} | {artist} | {track} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% |\n")
        
        # Топ 51-100
        md_content.append("\n---\n")
        md_content.append("\n## 📋 Треки 51-100\n")
        md_content.append("\n| # | Исполнитель | Трек | Доход (EUR) | % бюджета | Накопительный % |\n")
        md_content.append("|---|-------------|------|-------------|-----------|------------------|\n")
        
        for idx, (track_artist, row) in enumerate(self.results['top_100'].iloc[50:100].iterrows(), 51):
            artist = row.name[1] if isinstance(row.name, tuple) else 'Unknown'
            track = row.name[2] if isinstance(row.name, tuple) else track_artist
            revenue = row['Доход (EUR)']
            percent = row['% от бюджета']
            cumulative = row['Накопительный %']
            
            md_content.append(f"| {idx} | {artist} | {track} | {revenue:,.2f} | {percent:.2f}% | {cumulative:.2f}% |\n")
        
        md_content.append("\n---\n")
        md_content.append("\n*Отчет сгенерирован автоматически скриптом `analyze_top_tracks_q3.py`*\n")
        
        # Сохраняем
        md_file = output_path / 'TOP_100_TRACKS_Q3_2025.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.writelines(md_content)
        
        print(f"   ✓ {md_file.name}")


def main():
    """Основная функция"""
    print("🎵 Анализатор топ-100 треков Q3 2025")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = TopTracksQ3Analyzer(data_dir='data/processed')
    
    # Выполняем анализ
    analyzer.analyze_q3_tracks()
    
    if not analyzer.results:
        print("\n❌ Ошибка при анализе данных")
        return
    
    # Выводим отчет
    analyzer.print_report()
    
    # Сохраняем результаты
    analyzer.save_report()


if __name__ == '__main__':
    main()

