"""
Скрипт для генерации отчетов по всем артистам из Believe Digital
Анализирует данные из data/processed/1855874_704133_2025-10-01_2025-12-01.csv
"""

import pandas as pd
import os
from pathlib import Path
from collections import defaultdict
import json

# Пути к файлам
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "1855874_704133_2025-10-01_2025-12-01.csv"
REPORTS_DIR = BASE_DIR / "reports" / "believe_artists"
SUMMARY_DIR = BASE_DIR / "reports" / "believe_summary"

def load_believe_data():
    """Загружает данные из CSV файла Believe Digital"""
    print("Загрузка данных Believe Digital...")
    
    # Читаем CSV как строки сначала
    df = pd.read_csv(
        DATA_FILE,
        sep=';',
        encoding='utf-8',
        dtype=str
    )
    
    print(f"Загружено {len(df)} строк")
    print(f"Колонки: {df.columns.tolist()}")
    
    # Очищаем данные
    df['Исполнитель'] = df['Исполнитель'].str.strip().str.strip('"')
    df['Платформа'] = df['Платформа'].str.strip().str.strip('"')
    df['страна / регион'] = df['страна / регион'].str.strip().str.strip('"')
    df['Название трека'] = df['Название трека'].str.strip().str.strip('"')
    
    # Конвертируем числовые колонки (заменяем запятую на точку для европейского формата)
    df['Количество'] = df['Количество'].str.replace(',', '.').astype(float)
    df['Общий доход'] = df['Общий доход'].str.replace(',', '.').astype(float)
    df['Сумма вознаграждения'] = df['Сумма вознаграждения'].str.replace(',', '.').astype(float)
    
    return df

def analyze_artist(df, artist_name):
    """Анализирует данные для одного артиста"""
    
    # Фильтруем данные по артисту
    artist_data = df[df['Исполнитель'] == artist_name].copy()
    
    if len(artist_data) == 0:
        return None
    
    # 1) Суммарный доход в евро
    total_revenue = artist_data['Сумма вознаграждения'].sum()
    total_streams = artist_data['Количество'].sum()
    
    # 2) Топ 5 DSP (Digital Service Providers - музыкальные площадки)
    dsp_stats = artist_data.groupby('Платформа').agg({
        'Количество': 'sum',
        'Сумма вознаграждения': 'sum'
    }).reset_index()
    
    dsp_stats.columns = ['platform', 'streams', 'revenue']
    dsp_stats['percentage'] = (dsp_stats['revenue'] / total_revenue * 100).round(2)
    dsp_stats = dsp_stats.sort_values('revenue', ascending=False).head(5)
    
    # 3) География (топ 10 стран)
    geo_stats = artist_data.groupby('страна / регион').agg({
        'Количество': 'sum',
        'Сумма вознаграждения': 'sum'
    }).reset_index()
    
    geo_stats.columns = ['country', 'streams', 'revenue']
    geo_stats['percentage'] = (geo_stats['revenue'] / total_revenue * 100).round(2)
    geo_stats = geo_stats.sort_values('revenue', ascending=False).head(10)
    
    # 4) Самый популярный трек
    track_stats = artist_data.groupby('Название трека').agg({
        'Количество': 'sum',
        'Сумма вознаграждения': 'sum'
    }).reset_index()
    
    track_stats.columns = ['track', 'streams', 'revenue']
    top_track = track_stats.sort_values('streams', ascending=False).iloc[0] if len(track_stats) > 0 else None
    
    # Формируем результат
    result = {
        'artist_name': artist_name,
        'total_revenue_eur': round(total_revenue, 2),
        'total_streams': int(total_streams),
        'top_5_platforms': dsp_stats.to_dict('records'),
        'top_10_countries': geo_stats.to_dict('records'),
        'top_track': {
            'name': top_track['track'] if top_track is not None else '',
            'streams': int(top_track['streams']) if top_track is not None else 0,
            'revenue_eur': round(top_track['revenue'], 2) if top_track is not None else 0
        },
        'unique_tracks': len(artist_data['Название трека'].unique()),
        'unique_platforms': len(artist_data['Платформа'].unique()),
        'unique_countries': len(artist_data['страна / регион'].unique())
    }
    
    return result

def generate_markdown_report(artist_data):
    """Генерирует Markdown отчет для одного артиста"""
    
    md = f"""# ОТЧЕТ BELIEVE DIGITAL: {artist_data['artist_name']}

**Период:** Q4 2025 (Октябрь - Декабрь 2025)  
**Источник данных:** Believe Digital

---

## 📊 ОБЩАЯ СТАТИСТИКА

- **Суммарный доход:** €{artist_data['total_revenue_eur']:,.2f}
- **Всего стримов:** {artist_data['total_streams']:,}
- **Уникальных треков:** {artist_data['unique_tracks']}
- **Платформ:** {artist_data['unique_platforms']}
- **Стран:** {artist_data['unique_countries']}
- **Средняя цена за стрим:** €{(artist_data['total_revenue_eur'] / artist_data['total_streams']):.6f}

---

## 🎵 ТОП-5 ПЛАТФОРМ (DSP)

| # | Платформа | Стримы | Доход (EUR) | % от дохода |
|---|-----------|--------|-------------|-------------|
"""
    
    for idx, platform in enumerate(artist_data['top_5_platforms'], 1):
        streams_formatted = f"{int(platform['streams']):,}"
        revenue_formatted = f"€{platform['revenue']:,.2f}"
        md += f"| {idx} | {platform['platform']} | {streams_formatted} | {revenue_formatted} | {platform['percentage']}% |\n"
    
    md += f"""
---

## 🌍 ГЕОГРАФИЯ (ТОП-10 СТРАН)

| # | Страна | Стримы | Доход (EUR) | % от дохода |
|---|--------|--------|-------------|-------------|
"""
    
    for idx, country in enumerate(artist_data['top_10_countries'], 1):
        streams_formatted = f"{int(country['streams']):,}"
        revenue_formatted = f"€{country['revenue']:,.2f}"
        md += f"| {idx} | {country['country']} | {streams_formatted} | {revenue_formatted} | {country['percentage']}% |\n"
    
    md += f"""
---

## 🏆 САМЫЙ ПОПУЛЯРНЫЙ ТРЕК

**Название:** {artist_data['top_track']['name']}

- **Стримов:** {artist_data['top_track']['streams']:,}
- **Доход:** €{artist_data['top_track']['revenue_eur']:,.2f}
- **% от общего дохода артиста:** {(artist_data['top_track']['revenue_eur'] / artist_data['total_revenue_eur'] * 100):.2f}%

---

*Отчет сгенерирован автоматически*
"""
    
    return md

def generate_csv_summary(all_artists_data):
    """Генерирует CSV сводку по всем артистам"""
    
    summary_data = []
    for artist in all_artists_data:
        top_platform = artist['top_5_platforms'][0] if artist['top_5_platforms'] else {'platform': 'N/A', 'percentage': 0}
        top_country = artist['top_10_countries'][0] if artist['top_10_countries'] else {'country': 'N/A', 'percentage': 0}
        
        summary_data.append({
            'Artist': artist['artist_name'],
            'Total Revenue (EUR)': artist['total_revenue_eur'],
            'Total Streams': artist['total_streams'],
            'Unique Tracks': artist['unique_tracks'],
            'Top Platform': top_platform['platform'],
            'Top Platform %': top_platform['percentage'],
            'Top Country': top_country['country'],
            'Top Country %': top_country['percentage'],
            'Top Track': artist['top_track']['name'],
            'Top Track Streams': artist['top_track']['streams'],
            'Top Track Revenue': artist['top_track']['revenue_eur']
        })
    
    df_summary = pd.DataFrame(summary_data)
    df_summary = df_summary.sort_values('Total Revenue (EUR)', ascending=False)
    
    return df_summary

def main():
    """Главная функция"""
    
    print("=" * 80)
    print("ГЕНЕРАЦИЯ ОТЧЕТОВ BELIEVE DIGITAL ПО ВСЕМ АРТИСТАМ")
    print("=" * 80)
    
    # Создаем директории для отчетов
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Загружаем данные
    df = load_believe_data()
    
    # Получаем список всех артистов
    artists = df['Исполнитель'].unique()
    print(f"\nНайдено {len(artists)} уникальных артистов")
    
    # Анализируем каждого артиста
    all_artists_data = []
    
    for idx, artist in enumerate(artists, 1):
        print(f"\n[{idx}/{len(artists)}] Анализ артиста: {artist}")
        
        artist_data = analyze_artist(df, artist)
        
        if artist_data is None:
            print(f"  ⚠️  Нет данных для артиста {artist}")
            continue
        
        all_artists_data.append(artist_data)
        
        # Генерируем Markdown отчет
        md_content = generate_markdown_report(artist_data)
        
        # Сохраняем отчет (заменяем недопустимые символы в имени файла)
        safe_filename = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        md_path = REPORTS_DIR / f"{safe_filename}_report.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✅ Отчет сохранен: {md_path.name}")
        print(f"     Доход: €{artist_data['total_revenue_eur']:,.2f} | Стримы: {artist_data['total_streams']:,}")
    
    # Сохраняем JSON со всеми данными в summary
    json_path = SUMMARY_DIR / "all_artists_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_artists_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON данные сохранены: {json_path}")
    
    # Генерируем CSV сводку
    csv_summary = generate_csv_summary(all_artists_data)
    csv_path = SUMMARY_DIR / "artists_summary.csv"
    csv_summary.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ CSV сводка сохранена: {csv_path}")
    
    # Генерируем общий Markdown отчет
    master_md = f"""# СВОДНЫЙ ОТЧЕТ BELIEVE DIGITAL - ВСЕ АРТИСТЫ

**Период:** Q4 2025 (Октябрь - Декабрь 2025)  
**Всего артистов:** {len(all_artists_data)}

---

## ТОП-30 АРТИСТОВ ПО ДОХОДУ

| # | Артист | Доход (EUR) | Стримы | Треков | Топ платформа | Топ страна |
|---|--------|-------------|--------|--------|---------------|------------|
"""
    
    for idx, artist in enumerate(sorted(all_artists_data, key=lambda x: x['total_revenue_eur'], reverse=True)[:30], 1):
        top_platform = artist['top_5_platforms'][0]['platform'] if artist['top_5_platforms'] else 'N/A'
        top_country = artist['top_10_countries'][0]['country'] if artist['top_10_countries'] else 'N/A'
        
        master_md += f"| {idx} | {artist['artist_name']} | €{artist['total_revenue_eur']:,.2f} | {artist['total_streams']:,} | {artist['unique_tracks']} | {top_platform} | {top_country} |\n"
    
    master_md += "\n---\n\n*Детальные отчеты по каждому артисту находятся в папке `/reports/believe_artists/`*\n"
    
    master_path = SUMMARY_DIR / "README.md"
    with open(master_path, 'w', encoding='utf-8') as f:
        f.write(master_md)
    print(f"✅ Мастер-отчет сохранен: {master_path}")
    
    print("\n" + "=" * 80)
    print("✅ ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
    print(f"📁 Индивидуальные отчеты (.md): {REPORTS_DIR}")
    print(f"📁 Сводные отчеты (CSV/JSON): {SUMMARY_DIR}")
    print(f"📊 Проанализировано артистов: {len(all_artists_data)}")
    print(f"💰 Общий доход всех артистов: €{sum(a['total_revenue_eur'] for a in all_artists_data):,.2f}")
    print(f"🎵 Общее количество стримов: {sum(a['total_streams'] for a in all_artists_data):,}")
    print("=" * 80)

if __name__ == "__main__":
    main()

