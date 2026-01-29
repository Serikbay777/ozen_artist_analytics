#!/usr/bin/env python3
"""
Скрипт для анализа доходов по DSP (Digital Service Providers)
с разделением на российские и зарубежные платформы
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple
import json


class DSPRevenueAnalyzer:
    """Анализатор доходов по DSP платформам"""
    
    # Классификация DSP платформ
    RUSSIAN_DSP = {
        'Yandex',
        'Yandex Music',
        'VK Music',
        'UMA VK MUSIC',
        'UMA (Vkontakte)',
        'SberZvuk',
        'HITTER - Beeline Kazakhstan',
        'Zvuk',
    }
    
    FOREIGN_DSP = {
        'Spotify',
        'Apple Music',
        'YouTube Official Content',
        'YouTube UGC',
        'YouTube Music',
        'TikTok',
        'Facebook / Instagram',
        'Instagram',
        'Facebook',
        'Amazon Music',
        'Deezer',
        'Tidal',
        'NetEase',
        'iTunes Match',
        'iTunes',
        'Pandora',
        'SoundCloud',
        'Napster',
    }
    
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
    
    def classify_dsp(self, platform: str) -> str:
        """
        Классификация DSP на российские/зарубежные
        
        Args:
            platform: Название платформы
            
        Returns:
            'russian', 'foreign' или 'unknown'
        """
        if pd.isna(platform):
            return 'unknown'
        
        platform_str = str(platform).strip()
        
        # Проверяем точное совпадение
        if platform_str in self.RUSSIAN_DSP:
            return 'russian'
        if platform_str in self.FOREIGN_DSP:
            return 'foreign'
        
        # Проверяем частичное совпадение для российских
        for russian_dsp in self.RUSSIAN_DSP:
            if russian_dsp.lower() in platform_str.lower():
                return 'russian'
        
        # Проверяем частичное совпадение для зарубежных
        for foreign_dsp in self.FOREIGN_DSP:
            if foreign_dsp.lower() in platform_str.lower():
                return 'foreign'
        
        return 'unknown'
    
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
            Строка вида "Q1 2025" или "Unknown"
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
    
    def analyze_revenue(self) -> Dict:
        """
        Основной анализ доходов по DSP
        
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
        
        # Определяем названия колонок (могут быть на русском)
        platform_col = 'Платформа' if 'Платформа' in combined_df.columns else 'Platform'
        revenue_col = 'Сумма вознаграждения' if 'Сумма вознаграждения' in combined_df.columns else 'Revenue'
        total_revenue_col = 'Общий доход' if 'Общий доход' in combined_df.columns else 'Total Revenue'
        quantity_col = 'Количество' if 'Количество' in combined_df.columns else 'Quantity'
        report_month_col = 'Месяц отчета' if 'Месяц отчета' in combined_df.columns else 'Report Month'
        
        # Очищаем числовые колонки
        print("🧹 Очистка данных...")
        combined_df['revenue_clean'] = self.clean_numeric_column(combined_df, revenue_col)
        combined_df['total_revenue_clean'] = self.clean_numeric_column(combined_df, total_revenue_col)
        combined_df['quantity_clean'] = self.clean_numeric_column(combined_df, quantity_col)
        
        # Классифицируем DSP
        print("🏷️  Классификация платформ...")
        combined_df['dsp_type'] = combined_df[platform_col].apply(self.classify_dsp)
        
        # Определяем квартал и месяц
        print("📅 Определение кварталов и месяцев...")
        combined_df['quarter'] = combined_df[report_month_col].apply(self.get_quarter_from_date)
        combined_df['month'] = combined_df[report_month_col].apply(self.get_month_from_date)
        
        # Анализ по каждой платформе
        print("\n💰 Расчет доходов по платформам...")
        
        platform_stats = combined_df.groupby(platform_col).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum',
            'dsp_type': 'first'
        }).round(2)
        
        platform_stats.columns = ['Сумма вознаграждения (EUR)', 'Общий доход (EUR)', 'Количество', 'Тип DSP']
        platform_stats = platform_stats.sort_values('Сумма вознаграждения (EUR)', ascending=False)
        
        # Анализ по типу DSP (российские/зарубежные)
        dsp_type_stats = combined_df.groupby('dsp_type').agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        
        dsp_type_stats.columns = ['Сумма вознаграждения (EUR)', 'Общий доход (EUR)', 'Количество']
        
        # Анализ по кварталам
        print("📊 Расчет доходов по кварталам...")
        
        quarterly_stats = combined_df.groupby(['quarter', 'dsp_type']).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        
        quarterly_stats.columns = ['Сумма вознаграждения (EUR)', 'Общий доход (EUR)', 'Количество']
        
        # Сводная таблица по кварталам (только российские и зарубежные)
        quarterly_pivot = combined_df[combined_df['dsp_type'].isin(['russian', 'foreign'])].pivot_table(
            values='revenue_clean',
            index='quarter',
            columns='dsp_type',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        
        # Переименовываем колонки
        if 'russian' in quarterly_pivot.columns:
            quarterly_pivot.rename(columns={'russian': 'Российские DSP (EUR)'}, inplace=True)
        if 'foreign' in quarterly_pivot.columns:
            quarterly_pivot.rename(columns={'foreign': 'Зарубежные DSP (EUR)'}, inplace=True)
        
        # Добавляем общую сумму
        quarterly_pivot['Всего (EUR)'] = quarterly_pivot.sum(axis=1)
        
        # Сортируем по кварталам
        quarterly_pivot = quarterly_pivot.sort_index()
        
        # Анализ по месяцам
        print("📊 Расчет доходов по месяцам...")
        
        monthly_stats = combined_df.groupby(['month', 'dsp_type']).agg({
            'revenue_clean': 'sum',
            'total_revenue_clean': 'sum',
            'quantity_clean': 'sum'
        }).round(2)
        
        monthly_stats.columns = ['Сумма вознаграждения (EUR)', 'Общий доход (EUR)', 'Количество']
        
        # Сводная таблица по месяцам (только российские и зарубежные)
        monthly_pivot = combined_df[combined_df['dsp_type'].isin(['russian', 'foreign'])].pivot_table(
            values='revenue_clean',
            index='month',
            columns='dsp_type',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        
        # Переименовываем колонки
        if 'russian' in monthly_pivot.columns:
            monthly_pivot.rename(columns={'russian': 'Российские DSP (EUR)'}, inplace=True)
        if 'foreign' in monthly_pivot.columns:
            monthly_pivot.rename(columns={'foreign': 'Зарубежные DSP (EUR)'}, inplace=True)
        
        # Добавляем общую сумму
        monthly_pivot['Всего (EUR)'] = monthly_pivot.sum(axis=1)
        
        # Сортируем по месяцам
        monthly_pivot = monthly_pivot.sort_index()
        
        # Подсчет количества уникальных платформ
        unique_platforms = combined_df.groupby('dsp_type')[platform_col].nunique()
        
        self.results = {
            'platform_stats': platform_stats,
            'dsp_type_stats': dsp_type_stats,
            'unique_platforms': unique_platforms,
            'quarterly_stats': quarterly_stats,
            'quarterly_pivot': quarterly_pivot,
            'monthly_stats': monthly_stats,
            'monthly_pivot': monthly_pivot,
            'total_rows': len(combined_df),
            'combined_df': combined_df
        }
        
        return self.results
    
    def print_report(self) -> None:
        """Вывод отчета в консоль"""
        if not self.results:
            print("⚠️  Сначала выполните analyze_revenue()")
            return
        
        print("\n" + "="*80)
        print("📊 ОТЧЕТ ПО ДОХОДАМ DSP ПЛАТФОРМ")
        print("="*80)
        
        # Общая статистика
        print(f"\n📈 Общая статистика:")
        print(f"   Всего записей: {self.results['total_rows']:,}")
        
        # Статистика по типам DSP
        print(f"\n🌍 Разделение по типам DSP (за весь период):")
        print("-" * 80)
        
        dsp_type_stats = self.results['dsp_type_stats']
        
        for dsp_type in ['russian', 'foreign', 'unknown']:
            if dsp_type in dsp_type_stats.index:
                row = dsp_type_stats.loc[dsp_type]
                type_name = {
                    'russian': '🇷🇺 Российские DSP',
                    'foreign': '🌎 Зарубежные DSP',
                    'unknown': '❓ Неизвестные DSP'
                }[dsp_type]
                
                platforms_count = self.results['unique_platforms'].get(dsp_type, 0)
                
                print(f"\n{type_name} ({platforms_count} платформ):")
                print(f"   Сумма вознаграждения: {row['Сумма вознаграждения (EUR)']:,.2f} EUR")
                print(f"   Общий доход:          {row['Общий доход (EUR)']:,.2f} EUR")
                print(f"   Количество стримов:   {int(row['Количество']):,}")
        
        # Процентное соотношение
        total_revenue = dsp_type_stats['Сумма вознаграждения (EUR)'].sum()
        
        if total_revenue > 0:
            print(f"\n📊 Процентное соотношение доходов:")
            print("-" * 80)
            
            for dsp_type in ['russian', 'foreign']:
                if dsp_type in dsp_type_stats.index:
                    revenue = dsp_type_stats.loc[dsp_type, 'Сумма вознаграждения (EUR)']
                    percentage = (revenue / total_revenue) * 100
                    
                    type_name = '🇷🇺 Российские' if dsp_type == 'russian' else '🌎 Зарубежные'
                    bar = '█' * int(percentage / 2)
                    
                    print(f"{type_name:20} {percentage:6.2f}% {bar}")
        
        # Квартальная статистика
        print(f"\n\n📅 КВАРТАЛЬНАЯ СТАТИСТИКА:")
        print("="*80)
        
        quarterly_pivot = self.results['quarterly_pivot']
        
        if not quarterly_pivot.empty:
            print("\n💰 Доходы по кварталам:")
            print("-" * 80)
            print(f"{'Квартал':<15} {'Российские DSP':>18} {'Зарубежные DSP':>18} {'Всего':>15}")
            print("-" * 80)
            
            for quarter in quarterly_pivot.index:
                if quarter == 'Unknown':
                    continue
                    
                russian = quarterly_pivot.loc[quarter].get('Российские DSP (EUR)', 0)
                foreign = quarterly_pivot.loc[quarter].get('Зарубежные DSP (EUR)', 0)
                total = quarterly_pivot.loc[quarter].get('Всего (EUR)', 0)
                
                print(f"{quarter:<15} {russian:>15,.2f} € {foreign:>15,.2f} € {total:>15,.2f} €")
            
            # Проверка порога 15,000 EUR для зарубежных DSP
            print("\n" + "="*80)
            print("🎯 АНАЛИЗ ПОРОГА 15,000 EUR НА ЗАРУБЕЖНЫХ ПЛОЩАДКАХ")
            print("="*80)
            
            threshold = 15000
            
            if 'Зарубежные DSP (EUR)' in quarterly_pivot.columns:
                for quarter in quarterly_pivot.index:
                    if quarter == 'Unknown':
                        continue
                    
                    foreign_revenue = quarterly_pivot.loc[quarter, 'Зарубежные DSP (EUR)']
                    
                    if foreign_revenue >= threshold:
                        status = "✅ ДОСТИГНУТ"
                        percentage = 100
                    else:
                        status = "❌ НЕ ДОСТИГНУТ"
                        percentage = (foreign_revenue / threshold) * 100
                    
                    remaining = max(0, threshold - foreign_revenue)
                    bar = '█' * int(percentage / 5)
                    
                    print(f"\n{quarter}:")
                    print(f"  Доход: {foreign_revenue:,.2f} EUR")
                    print(f"  Прогресс: [{bar:<20}] {percentage:.1f}%")
                    print(f"  Статус: {status}")
                    if remaining > 0:
                        print(f"  До порога: {remaining:,.2f} EUR")
            
            # Прогноз
            print("\n" + "="*80)
            print("📈 ПРОГНОЗ")
            print("="*80)
            
            if 'Зарубежные DSP (EUR)' in quarterly_pivot.columns:
                # Берем только известные кварталы
                known_quarters = quarterly_pivot[quarterly_pivot.index != 'Unknown']
                
                if len(known_quarters) > 0:
                    avg_foreign = known_quarters['Зарубежные DSP (EUR)'].mean()
                    
                    print(f"\nСредний доход с зарубежных DSP за квартал: {avg_foreign:,.2f} EUR")
                    
                    if avg_foreign >= threshold:
                        print(f"✅ В среднем вы ПРЕВЫШАЕТЕ порог 15,000 EUR на {avg_foreign - threshold:,.2f} EUR")
                    else:
                        print(f"⚠️  В среднем вы НЕ ДОСТИГАЕТЕ порога 15,000 EUR")
                        print(f"   Не хватает: {threshold - avg_foreign:,.2f} EUR в квартал")
                        growth_needed = ((threshold / avg_foreign) - 1) * 100
                        print(f"   Необходимый рост: {growth_needed:.1f}%")
        
        # Месячная статистика
        print(f"\n\n📅 МЕСЯЧНАЯ СТАТИСТИКА:")
        print("="*80)
        
        monthly_pivot = self.results['monthly_pivot']
        
        if not monthly_pivot.empty:
            print("\n💰 Доходы по месяцам:")
            print("-" * 80)
            print(f"{'Месяц':<12} {'Российские DSP':>18} {'Зарубежные DSP':>18} {'Всего':>15}")
            print("-" * 80)
            
            month_names = {
                '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
                '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
                '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
            }
            
            for month in monthly_pivot.index:
                if month == 'Unknown':
                    continue
                
                try:
                    year, month_num = month.split('-')
                    month_display = f"{month_names.get(month_num, month_num)} {year}"
                except:
                    month_display = month
                    
                russian = monthly_pivot.loc[month].get('Российские DSP (EUR)', 0)
                foreign = monthly_pivot.loc[month].get('Зарубежные DSP (EUR)', 0)
                total = monthly_pivot.loc[month].get('Всего (EUR)', 0)
                
                print(f"{month_display:<12} {russian:>15,.2f} € {foreign:>15,.2f} € {total:>15,.2f} €")
            
            # Проверка порога 15,000 EUR для зарубежных DSP по месяцам
            print("\n" + "="*80)
            print("🎯 АНАЛИЗ ПОРОГА 15,000 EUR НА ЗАРУБЕЖНЫХ ПЛОЩАДКАХ (ПО МЕСЯЦАМ)")
            print("="*80)
            
            threshold = 15000
            
            if 'Зарубежные DSP (EUR)' in monthly_pivot.columns:
                for month in monthly_pivot.index:
                    if month == 'Unknown':
                        continue
                    
                    try:
                        year, month_num = month.split('-')
                        month_display = f"{month_names.get(month_num, month_num)} {year}"
                    except:
                        month_display = month
                    
                    foreign_revenue = monthly_pivot.loc[month, 'Зарубежные DSP (EUR)']
                    
                    if foreign_revenue >= threshold:
                        status = "✅ ДОСТИГНУТ"
                        percentage = 100
                    else:
                        status = "❌ НЕ ДОСТИГНУТ"
                        percentage = (foreign_revenue / threshold) * 100
                    
                    remaining = max(0, threshold - foreign_revenue)
                    bar = '█' * int(percentage / 5)
                    
                    print(f"\n{month_display}:")
                    print(f"  Доход: {foreign_revenue:,.2f} EUR")
                    print(f"  Прогресс: [{bar:<20}] {percentage:.1f}%")
                    print(f"  Статус: {status}")
                    if remaining > 0:
                        print(f"  До порога: {remaining:,.2f} EUR")
            
            # Прогноз по месяцам
            print("\n" + "="*80)
            print("📈 МЕСЯЧНЫЙ ПРОГНОЗ")
            print("="*80)
            
            if 'Зарубежные DSP (EUR)' in monthly_pivot.columns:
                # Берем только известные месяцы
                known_months = monthly_pivot[monthly_pivot.index != 'Unknown']
                
                if len(known_months) > 0:
                    avg_foreign = known_months['Зарубежные DSP (EUR)'].mean()
                    min_foreign = known_months['Зарубежные DSP (EUR)'].min()
                    max_foreign = known_months['Зарубежные DSP (EUR)'].max()
                    
                    print(f"\nСтатистика доходов с зарубежных DSP:")
                    print(f"  Средний доход за месяц: {avg_foreign:,.2f} EUR")
                    print(f"  Минимум: {min_foreign:,.2f} EUR")
                    print(f"  Максимум: {max_foreign:,.2f} EUR")
                    
                    if avg_foreign >= threshold:
                        print(f"\n✅ В среднем вы ПРЕВЫШАЕТЕ порог 15,000 EUR на {avg_foreign - threshold:,.2f} EUR")
                    else:
                        print(f"\n⚠️  В среднем вы НЕ ДОСТИГАЕТЕ порога 15,000 EUR")
                        print(f"   Не хватает: {threshold - avg_foreign:,.2f} EUR в месяц")
                        growth_needed = ((threshold / avg_foreign) - 1) * 100
                        print(f"   Необходимый рост: {growth_needed:.1f}%")
                    
                    # Считаем сколько месяцев достигли порога
                    months_above_threshold = (known_months['Зарубежные DSP (EUR)'] >= threshold).sum()
                    total_months = len(known_months)
                    
                    print(f"\n📊 Достижение порога:")
                    print(f"   {months_above_threshold} из {total_months} месяцев достигли 15,000 EUR")
                    print(f"   Процент успеха: {(months_above_threshold / total_months * 100):.1f}%")
        
        # Топ-10 платформ
        print(f"\n\n🏆 ТОП-10 платформ по доходам:")
        print("-" * 80)
        
        platform_stats = self.results['platform_stats'].head(10)
        
        for idx, (platform, row) in enumerate(platform_stats.iterrows(), 1):
            dsp_icon = '🇷🇺' if row['Тип DSP'] == 'russian' else '🌎' if row['Тип DSP'] == 'foreign' else '❓'
            print(f"{idx:2}. {dsp_icon} {platform[:40]:40} {row['Сумма вознаграждения (EUR)']:>12,.2f} EUR")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str = 'reports') -> None:
        """
        Сохранение отчета в файлы
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        if not self.results:
            print("⚠️  Сначала выполните analyze_revenue()")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Сохранение отчетов в {output_dir}/...")
        
        # 1. Сохраняем детальную статистику по платформам
        platform_report = output_path / 'dsp_platform_revenue.csv'
        self.results['platform_stats'].to_csv(platform_report, encoding='utf-8-sig')
        print(f"   ✓ {platform_report.name}")
        
        # 2. Сохраняем сводку по типам DSP
        dsp_type_report = output_path / 'dsp_type_summary.csv'
        self.results['dsp_type_stats'].to_csv(dsp_type_report, encoding='utf-8-sig')
        print(f"   ✓ {dsp_type_report.name}")
        
        # 2.5. Сохраняем квартальную статистику
        quarterly_report = output_path / 'dsp_quarterly_revenue.csv'
        self.results['quarterly_pivot'].to_csv(quarterly_report, encoding='utf-8-sig')
        print(f"   ✓ {quarterly_report.name}")
        
        # 2.6. Сохраняем месячную статистику
        monthly_report = output_path / 'dsp_monthly_revenue.csv'
        self.results['monthly_pivot'].to_csv(monthly_report, encoding='utf-8-sig')
        print(f"   ✓ {monthly_report.name}")
        
        # 3. Сохраняем JSON с результатами
        json_report = output_path / 'dsp_revenue_summary.json'
        
        # Квартальные данные
        quarterly_data = {}
        threshold = 15000
        
        if 'Зарубежные DSP (EUR)' in self.results['quarterly_pivot'].columns:
            for quarter in self.results['quarterly_pivot'].index:
                if quarter == 'Unknown':
                    continue
                
                foreign_revenue = float(self.results['quarterly_pivot'].loc[quarter, 'Зарубежные DSP (EUR)'])
                russian_revenue = float(self.results['quarterly_pivot'].loc[quarter].get('Российские DSP (EUR)', 0))
                
                quarterly_data[quarter] = {
                    'foreign_revenue': foreign_revenue,
                    'russian_revenue': russian_revenue,
                    'total_revenue': foreign_revenue + russian_revenue,
                    'threshold_15k_reached': foreign_revenue >= threshold,
                    'remaining_to_threshold': max(0, threshold - foreign_revenue),
                    'percentage_of_threshold': (foreign_revenue / threshold) * 100
                }
        
        # Месячные данные
        monthly_data = {}
        
        if 'Зарубежные DSP (EUR)' in self.results['monthly_pivot'].columns:
            for month in self.results['monthly_pivot'].index:
                if month == 'Unknown':
                    continue
                
                foreign_revenue = float(self.results['monthly_pivot'].loc[month, 'Зарубежные DSP (EUR)'])
                russian_revenue = float(self.results['monthly_pivot'].loc[month].get('Российские DSP (EUR)', 0))
                
                monthly_data[month] = {
                    'foreign_revenue': foreign_revenue,
                    'russian_revenue': russian_revenue,
                    'total_revenue': foreign_revenue + russian_revenue,
                    'threshold_15k_reached': foreign_revenue >= threshold,
                    'remaining_to_threshold': max(0, threshold - foreign_revenue),
                    'percentage_of_threshold': (foreign_revenue / threshold) * 100
                }
        
        summary = {
            'total_rows': self.results['total_rows'],
            'dsp_type_summary': {
                dsp_type: {
                    'revenue': float(row['Сумма вознаграждения (EUR)']),
                    'total_revenue': float(row['Общий доход (EUR)']),
                    'quantity': int(row['Количество']),
                    'platforms_count': int(self.results['unique_platforms'].get(dsp_type, 0))
                }
                for dsp_type, row in self.results['dsp_type_stats'].iterrows()
            },
            'quarterly_analysis': quarterly_data,
            'monthly_analysis': monthly_data,
            'threshold_check': {
                'threshold': threshold,
                'currency': 'EUR',
                'description': 'Порог для зарубежных DSP (месячный)'
            },
            'top_10_platforms': [
                {
                    'platform': platform,
                    'revenue': float(row['Сумма вознаграждения (EUR)']),
                    'total_revenue': float(row['Общий доход (EUR)']),
                    'quantity': int(row['Количество']),
                    'type': row['Тип DSP']
                }
                for platform, row in self.results['platform_stats'].head(10).iterrows()
            ]
        }
        
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"   ✓ {json_report.name}")
        
        # 4. Сохраняем полные данные с классификацией
        full_data_report = output_path / 'dsp_full_data_classified.csv'
        
        # Выбираем только нужные колонки
        columns_to_save = [
            col for col in self.results['combined_df'].columns 
            if col not in ['revenue_clean', 'total_revenue_clean', 'quantity_clean']
        ]
        
        self.results['combined_df'][columns_to_save].to_csv(
            full_data_report, 
            encoding='utf-8-sig',
            index=False
        )
        print(f"   ✓ {full_data_report.name}")
        
        print(f"\n✅ Все отчеты сохранены в {output_dir}/")


def main():
    """Основная функция"""
    print("🎵 Анализатор доходов DSP платформ")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = DSPRevenueAnalyzer(data_dir='data/processed')
    
    # Загружаем данные
    print("\n📂 Загрузка данных...")
    analyzer.load_csv_files()
    
    if not analyzer.dataframes:
        print("\n❌ Не найдено CSV файлов для анализа")
        return
    
    # Выполняем анализ
    analyzer.analyze_revenue()
    
    # Выводим отчет
    analyzer.print_report()
    
    # Сохраняем результаты
    analyzer.save_report()


if __name__ == '__main__':
    main()

