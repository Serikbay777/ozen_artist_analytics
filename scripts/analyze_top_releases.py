"""
Script to analyze top 100 releases by revenue from õzen catalog data
"""

import pandas as pd
import glob
import os
from datetime import datetime
import json

def load_all_data():
    """Load all data files from the data directory"""
    data_files = glob.glob('data/*.csv')
    # Exclude processed folder
    data_files = [f for f in data_files if 'processed' not in f]
    
    print(f"Found {len(data_files)} data files")
    
    all_data = []
    for file in data_files:
        print(f"Loading {file}...")
        try:
            df = pd.read_csv(file, sep=';')
            all_data.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal rows loaded: {len(combined_df):,}")
    
    return combined_df

def clean_numeric_column(series):
    """Convert comma-separated decimal numbers to floats"""
    return series.astype(str).str.replace(',', '.').astype(float)

def analyze_top_releases(df):
    """Analyze and return top 100 releases by revenue"""
    
    # Clean numeric columns
    print("\nCleaning numeric columns...")
    df['Количество'] = clean_numeric_column(df['Количество'])
    df['Сумма вознаграждения'] = clean_numeric_column(df['Сумма вознаграждения'])
    df['Общий доход'] = clean_numeric_column(df['Общий доход'])
    
    # Group by release (UPC + Название релиза) and aggregate
    print("\nGrouping by release...")
    release_stats = df.groupby(['UPC', 'Название релиза', 'Исполнитель']).agg({
        'Сумма вознаграждения': 'sum',
        'Общий доход': 'sum',
        'Количество': 'sum',
        'ISRC': 'first',  # Get first ISRC as representative
        'Платформа': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown',  # Most common platform
        'Месяц продажи': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    release_stats.columns = ['UPC', 'Название релиза', 'Исполнитель', 
                              'Сумма вознаграждения', 'Общий доход', 'Количество', 'ISRC',
                              'Главная платформа', 'Первая продажа', 'Последняя продажа']
    
    # Sort by revenue (Сумма вознаграждения) descending
    top_releases = release_stats.sort_values('Сумма вознаграждения', ascending=False).head(100)
    
    # Add rank
    top_releases.insert(0, 'Ранг', range(1, len(top_releases) + 1))
    
    # Round numeric columns
    top_releases['Сумма вознаграждения'] = top_releases['Сумма вознаграждения'].round(2)
    top_releases['Общий доход'] = top_releases['Общий доход'].round(2)
    top_releases['Количество'] = top_releases['Количество'].round(0).astype(int)
    
    return top_releases

def create_report(top_releases):
    """Create markdown report"""
    
    report = f"""# TOP 100 РЕЛИЗОВ ПО ПРИБЫЛИ - КАТАЛОГ ÕZEN

**Дата создания отчета:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Обзор

Данный отчет представляет топ-100 релизов по сумме вознаграждения из всего каталога õzen.

### Ключевые метрики

- **Всего релизов в топ-100:** {len(top_releases)}
- **Общая сумма вознаграждения:** €{top_releases['Сумма вознаграждения'].sum():,.2f}
- **Общий доход:** €{top_releases['Общий доход'].sum():,.2f}
- **Общее количество продаж/стримов:** {top_releases['Количество'].sum():,}

### Топ-10 релизов

| Ранг | Исполнитель | Название релиза | UPC | ISRC | Сумма вознаграждения (€) | Количество |
|------|-------------|-----------------|-----|------|-------------------------|-----------|
"""
    
    # Add top 10 to markdown
    for _, row in top_releases.head(10).iterrows():
        report += f"| {row['Ранг']} | {row['Исполнитель']} | {row['Название релиза']} | {row['UPC']} | {row['ISRC']} | €{row['Сумма вознаграждения']:,.2f} | {row['Количество']:,} |\n"
    
    report += "\n\n## Статистика по исполнителям\n\n"
    
    # Artist statistics
    artist_stats = top_releases.groupby('Исполнитель').agg({
        'Сумма вознаграждения': 'sum',
        'Количество': 'sum',
        'Название релиза': 'count'
    }).sort_values('Сумма вознаграждения', ascending=False).head(20)
    
    report += "### Топ-20 исполнителей в топ-100 релизов\n\n"
    report += "| Исполнитель | Релизов в топ-100 | Сумма вознаграждения (€) | Количество продаж/стримов |\n"
    report += "|-------------|-------------------|-------------------------|---------------------------|\n"
    
    for artist, row in artist_stats.iterrows():
        report += f"| {artist} | {int(row['Название релиза'])} | €{row['Сумма вознаграждения']:,.2f} | {int(row['Количество']):,} |\n"
    
    report += "\n\n## Полный список топ-100 релизов\n\n"
    report += "Полный список с детализацией доступен в CSV файле `reports/top_100_releases_ozen.csv`\n\n"
    
    # Distribution analysis
    report += "## Анализ распределения доходов\n\n"
    report += f"- **Топ-10 релизов приносят:** €{top_releases.head(10)['Сумма вознаграждения'].sum():,.2f} ({top_releases.head(10)['Сумма вознаграждения'].sum() / top_releases['Сумма вознаграждения'].sum() * 100:.1f}%)\n"
    report += f"- **Топ-25 релизов приносят:** €{top_releases.head(25)['Сумма вознаграждения'].sum():,.2f} ({top_releases.head(25)['Сумма вознаграждения'].sum() / top_releases['Сумма вознаграждения'].sum() * 100:.1f}%)\n"
    report += f"- **Топ-50 релизов приносят:** €{top_releases.head(50)['Сумма вознаграждения'].sum():,.2f} ({top_releases.head(50)['Сумма вознаграждения'].sum() / top_releases['Сумма вознаграждения'].sum() * 100:.1f}%)\n\n"
    
    return report

def main():
    print("=" * 80)
    print("АНАЛИЗ ТОП-100 РЕЛИЗОВ ПО ПРИБЫЛИ - КАТАЛОГ ÕZEN")
    print("=" * 80)
    
    # Load data
    df = load_all_data()
    
    # Analyze top releases
    top_releases = analyze_top_releases(df)
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Save to CSV
    csv_path = 'reports/top_100_releases_ozen.csv'
    top_releases.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ CSV report saved to: {csv_path}")
    
    # Create and save markdown report
    report = create_report(top_releases)
    md_path = 'reports/TOP_100_RELEASES_OZEN.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Markdown report saved to: {md_path}")
    
    # Save summary as JSON
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_releases': int(len(top_releases)),
        'total_revenue': float(top_releases['Сумма вознаграждения'].sum()),
        'total_income': float(top_releases['Общий доход'].sum()),
        'total_quantity': int(top_releases['Количество'].sum()),
        'top_10_revenue': float(top_releases.head(10)['Сумма вознаграждения'].sum()),
        'top_release': {
            'artist': str(top_releases.iloc[0]['Исполнитель']),
            'title': str(top_releases.iloc[0]['Название релиза']),
            'upc': str(top_releases.iloc[0]['UPC']),
            'isrc': str(top_releases.iloc[0]['ISRC']),
            'revenue': float(top_releases.iloc[0]['Сумма вознаграждения'])
        }
    }
    
    json_path = 'reports/top_100_releases_summary.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON summary saved to: {json_path}")
    
    print("\n" + "=" * 80)
    print("PREVIEW - TOP 10 RELEASES")
    print("=" * 80)
    print(top_releases.head(10).to_string(index=False))
    
    print("\n✓ Analysis complete!")

if __name__ == '__main__':
    main()

