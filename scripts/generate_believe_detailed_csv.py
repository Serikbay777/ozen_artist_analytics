"""
Скрипт для генерации детального CSV отчета по всем артистам из Believe Digital
"""

import json
from pathlib import Path
import pandas as pd

# Пути к файлам
BASE_DIR = Path(__file__).parent.parent
JSON_FILE = BASE_DIR / "reports" / "believe_summary" / "all_artists_data.json"
OUTPUT_CSV = BASE_DIR / "reports" / "believe_summary" / "BELIEVE_ARTISTS_DETAILED_REPORT.csv"

def main():
    """Главная функция"""
    
    print("=" * 80)
    print("ГЕНЕРАЦИЯ ДЕТАЛЬНОГО CSV ОТЧЕТА")
    print("=" * 80)
    
    # Читаем JSON данные
    print(f"\nЗагрузка данных из {JSON_FILE.name}...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        artists_data = json.load(f)
    
    print(f"Загружено {len(artists_data)} артистов")
    
    # Формируем детальные строки
    detailed_rows = []
    
    for artist in artists_data:
        # Базовая информация
        row = {
            'Артист': artist['artist_name'],
            'Общий доход (EUR)': round(artist['total_revenue_eur'], 2),
            'Всего стримов': int(artist['total_streams']),
            'Уникальных треков': artist['unique_tracks'],
            'Платформ': artist['unique_platforms'],
            'Стран': artist['unique_countries'],
            'Средняя цена за стрим (EUR)': round(artist['total_revenue_eur'] / artist['total_streams'], 6) if artist['total_streams'] > 0 else 0,
        }
        
        # Топ трек
        row['Топ трек'] = artist['top_track']['name']
        row['Топ трек - стримы'] = int(artist['top_track']['streams'])
        row['Топ трек - доход (EUR)'] = round(artist['top_track']['revenue_eur'], 2)
        row['Топ трек - % дохода'] = round((artist['top_track']['revenue_eur'] / artist['total_revenue_eur'] * 100), 2) if artist['total_revenue_eur'] > 0 else 0
        
        # Топ-5 платформ
        for i in range(5):
            if i < len(artist['top_5_platforms']):
                platform = artist['top_5_platforms'][i]
                row[f'Платформа #{i+1}'] = platform['platform']
                row[f'Платформа #{i+1} - стримы'] = int(platform['streams'])
                row[f'Платформа #{i+1} - доход (EUR)'] = round(platform['revenue'], 2)
                row[f'Платформа #{i+1} - %'] = platform['percentage']
            else:
                row[f'Платформа #{i+1}'] = ''
                row[f'Платформа #{i+1} - стримы'] = 0
                row[f'Платформа #{i+1} - доход (EUR)'] = 0
                row[f'Платформа #{i+1} - %'] = 0
        
        # Топ-5 стран
        for i in range(5):
            if i < len(artist['top_10_countries']):
                country = artist['top_10_countries'][i]
                row[f'Страна #{i+1}'] = country['country']
                row[f'Страна #{i+1} - стримы'] = int(country['streams'])
                row[f'Страна #{i+1} - доход (EUR)'] = round(country['revenue'], 2)
                row[f'Страна #{i+1} - %'] = country['percentage']
            else:
                row[f'Страна #{i+1}'] = ''
                row[f'Страна #{i+1} - стримы'] = 0
                row[f'Страна #{i+1} - доход (EUR)'] = 0
                row[f'Страна #{i+1} - %'] = 0
        
        detailed_rows.append(row)
    
    # Создаем DataFrame и сортируем по доходу
    df = pd.DataFrame(detailed_rows)
    df = df.sort_values('Общий доход (EUR)', ascending=False)
    
    # Сохраняем в CSV
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')  # utf-8-sig для Excel
    
    print(f"\n✅ Детальный CSV отчет сохранен: {OUTPUT_CSV}")
    print(f"📊 Всего строк: {len(df)}")
    print(f"📋 Всего колонок: {len(df.columns)}")
    
    # Статистика
    print("\n" + "=" * 80)
    print("ОБЩАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего артистов: {len(artists_data)}")
    print(f"Общий доход: €{df['Общий доход (EUR)'].sum():,.2f}")
    print(f"Общее количество стримов: {df['Всего стримов'].sum():,}")
    print(f"Всего уникальных треков: {df['Уникальных треков'].sum():,}")
    print(f"\nСредний доход на артиста: €{df['Общий доход (EUR)'].mean():,.2f}")
    print(f"Медианный доход артиста: €{df['Общий доход (EUR)'].median():,.2f}")
    print(f"Средние стримы на артиста: {int(df['Всего стримов'].mean()):,}")
    print(f"Медианные стримы артиста: {int(df['Всего стримов'].median()):,}")
    
    # Топ-10 артистов
    print("\n" + "=" * 80)
    print("ТОП-10 АРТИСТОВ ПО ДОХОДУ")
    print("=" * 80)
    for idx, row in df.head(10).iterrows():
        print(f"{row.name + 1:2d}. {row['Артист']:<40} €{row['Общий доход (EUR)']:>10,.2f} | {row['Всего стримов']:>12,} стримов")
    
    print("\n" + "=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)

if __name__ == "__main__":
    main()

