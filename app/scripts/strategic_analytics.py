import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("📥 Загрузка данных...")
df = pd.read_pickle('/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/data/processed/all_believe_data.pkl')

# Подготовка
df['year'] = df['Месяц отчета'].dt.year
df['month'] = df['Месяц отчета'].dt.month
df['year_month'] = df['Месяц отчета'].dt.to_period('M')
df['release_date'] = df.groupby(['Исполнитель', 'Название трека'])['Месяц отчета'].transform('min')
df['track_age_months'] = ((df['Месяц отчета'] - df['release_date']).dt.days / 30).round(0)

total_revenue = df['Сумма вознаграждения'].sum()
total_streams = df['Количество'].sum()

print("=" * 80)
print("🎯 СТРАТЕГИЧЕСКИЙ АНАЛИЗ И МАТРИЦА РОСТА")
print("=" * 80)

# ============================================================================
# 1. ARPU И ДЕТАЛИЗАЦИЯ ПО АРТИСТАМ
# ============================================================================
print("\n" + "=" * 80)
print("💰 ARPU И ЭФФЕКТИВНОСТЬ АРТИСТОВ")
print("=" * 80)

artist_stats = df.groupby('Исполнитель').agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum',
    'Название трека': 'nunique',
    'Платформа': 'nunique',
    'страна / регион': 'nunique',
    'year_month': 'nunique'
}).reset_index()

artist_stats.columns = ['Артист', 'Выручка', 'Стримы', 'Треков', 'Платформ', 'Стран', 'Активных_месяцев']
artist_stats['CPM'] = (artist_stats['Выручка'] / artist_stats['Стримы'] * 1000)
artist_stats['Выручка_на_трек'] = artist_stats['Выручка'] / artist_stats['Треков']
artist_stats['Выручка_в_месяц'] = artist_stats['Выручка'] / artist_stats['Активных_месяцев']
artist_stats['Стримы_на_трек'] = artist_stats['Стримы'] / artist_stats['Треков']

# Топ-20 по ARPU (выручка на трек)
print("\n🏆 ТОП-20 АРТИСТОВ ПО ЭФФЕКТИВНОСТИ (ВЫРУЧКА НА ТРЕК):")
top_arpu = artist_stats[artist_stats['Треков'] >= 3].sort_values('Выручка_на_трек', ascending=False).head(20)
for _, row in top_arpu.iterrows():
    print(f"{row['Артист']}")
    print(f"   💰 €{row['Выручка_на_трек']:,.0f}/трек | 🎵 {row['Треков']} треков | Всего: €{row['Выручка']:,.0f}")
    print(f"   📊 CPM: €{row['CPM']:.3f} | 🎧 {row['Стримы_на_трек']/1e6:.1f}M стримов/трек")

# Активность
print("\n📈 ТОП-20 ПО ЕЖЕМЕСЯЧНОЙ ВЫРУЧКЕ:")
top_monthly = artist_stats.sort_values('Выручка_в_месяц', ascending=False).head(20)
for _, row in top_monthly.iterrows():
    print(f"{row['Артист']}: €{row['Выручка_в_месяц']:,.0f}/мес | {row['Активных_месяцев']} мес | Всего: €{row['Выручка']:,.0f}")

# ============================================================================
# 2. ВОЗРАСТ ТРЕКОВ И EVERGREEN VS VIRAL
# ============================================================================
print("\n" + "=" * 80)
print("⏳ АНАЛИЗ ВОЗРАСТА ТРЕКОВ")
print("=" * 80)

# Группировка по возрасту
track_age_analysis = df.groupby(['Исполнитель', 'Название трека']).agg({
    'release_date': 'first',
    'Месяц отчета': 'max',
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum',
    'year_month': 'nunique'
}).reset_index()

track_age_analysis['age_months'] = ((track_age_analysis['Месяц отчета'] - track_age_analysis['release_date']).dt.days / 30).round(0)
track_age_analysis['revenue_per_month'] = track_age_analysis['Сумма вознаграждения'] / track_age_analysis['year_month']

# Категории
def categorize_track(row):
    age = row['age_months']
    rpm = row['revenue_per_month']
    
    if age <= 6:
        return 'Новый релиз'
    elif age <= 12:
        return 'Молодой'
    elif age <= 24:
        return 'Зрелый'
    else:
        if rpm > 100:
            return 'Evergreen'
        else:
            return 'Старый'

track_age_analysis['Категория'] = track_age_analysis.apply(categorize_track, axis=1)

print("\n📊 РАСПРЕДЕЛЕНИЕ ТРЕКОВ ПО ВОЗРАСТУ:")
category_stats = track_age_analysis.groupby('Категория').agg({
    'Название трека': 'count',
    'Сумма вознаграждения': 'sum',
    'revenue_per_month': 'mean'
}).reset_index()
category_stats.columns = ['Категория', 'Треков', 'Выручка', 'Средняя_выручка_в_месяц']

for _, row in category_stats.iterrows():
    pct = (row['Выручка'] / total_revenue) * 100
    print(f"{row['Категория']}: {row['Треков']} треков | €{row['Выручка']:,.0f} ({pct:.1f}%) | €{row['Средняя_выручка_в_месяц']:.0f}/мес")

print("\n🌟 ТОП-15 EVERGREEN ТРЕКОВ:")
evergreen = track_age_analysis[track_age_analysis['Категория'] == 'Evergreen'].sort_values('Сумма вознаграждения', ascending=False).head(15)
for _, row in evergreen.iterrows():
    print(f"{row['Исполнитель']} - {row['Название трека']}")
    print(f"   💰 €{row['Сумма вознаграждения']:,.0f} | ⏱️  {row['age_months']:.0f} мес | €{row['revenue_per_month']:,.0f}/мес")

# ============================================================================
# 3. CPM ПО СТРАНЕ + ПЛАТФОРМА (ДЕТАЛИЗАЦИЯ)
# ============================================================================
print("\n" + "=" * 80)
print("🌍 CPM ПО СТРАНЕ × ПЛАТФОРМА")
print("=" * 80)

# Топ-10 стран и платформ
top_countries = df.groupby('страна / регион')['Сумма вознаграждения'].sum().nlargest(10).index
top_platforms = df.groupby('Платформа')['Сумма вознаграждения'].sum().nlargest(10).index

country_platform_cpm = df[
    (df['страна / регион'].isin(top_countries)) & 
    (df['Платформа'].isin(top_platforms))
].groupby(['страна / регион', 'Платформа']).agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum'
}).reset_index()

country_platform_cpm['CPM'] = (country_platform_cpm['Сумма вознаграждения'] / country_platform_cpm['Количество'] * 1000)
country_platform_cpm = country_platform_cpm[country_platform_cpm['Количество'] > 10000]

print("\n💎 ТОП-20 КОМБИНАЦИЙ СТРАНА×ПЛАТФОРМА ПО CPM:")
top_combos = country_platform_cpm.sort_values('CPM', ascending=False).head(20)
for _, row in top_combos.iterrows():
    print(f"{row['страна / регион']} × {row['Платформа']}")
    print(f"   💰 CPM: €{row['CPM']:.3f} | €{row['Сумма вознаграждения']:,.0f} | {row['Количество']/1e6:.1f}M стримов")

# ============================================================================
# 4. ПОТЕНЦИАЛ НЕДОИСПОЛЬЗОВАННЫХ КАНАЛОВ
# ============================================================================
print("\n" + "=" * 80)
print("💎 ПОТЕНЦИАЛ НЕДОИСПОЛЬЗОВАННЫХ КАНАЛОВ")
print("=" * 80)

# Низкий CPM, высокие стримы
low_cpm_analysis = df.groupby(['Платформа', 'страна / регион']).agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum'
}).reset_index()

low_cpm_analysis['CPM'] = (low_cpm_analysis['Сумма вознаграждения'] / low_cpm_analysis['Количество'] * 1000)
low_cpm_analysis = low_cpm_analysis[low_cpm_analysis['Количество'] > 1e6]  # Минимум 1M стримов

# Средний CPM по платформе
avg_platform_cpm = df.groupby('Платформа').apply(
    lambda x: (x['Сумма вознаграждения'].sum() / x['Количество'].sum() * 1000) if x['Количество'].sum() > 0 else 0
)

print("\n⚠️ ТОП-20 УПУЩЕННЫХ ВОЗМОЖНОСТЕЙ (Высокие стримы, низкий CPM):")
for platform in low_cpm_analysis['Платформа'].unique()[:10]:
    platform_data = low_cpm_analysis[low_cpm_analysis['Платформа'] == platform]
    avg_cpm = avg_platform_cpm.get(platform, 0)
    
    for _, row in platform_data.nsmallest(3, 'CPM').iterrows():
        if row['CPM'] < avg_cpm * 0.5:  # CPM ниже 50% от среднего
            potential_revenue = (row['Количество'] / 1000) * avg_cpm
            lost_revenue = potential_revenue - row['Сумма вознаграждения']
            
            if lost_revenue > 500:  # Потенциал больше €500
                print(f"{row['Платформа']} × {row['страна / регион']}")
                print(f"   📊 Текущий CPM: €{row['CPM']:.3f} | Средний: €{avg_cpm:.3f}")
                print(f"   💰 Текущая выручка: €{row['Сумма вознаграждения']:,.0f}")
                print(f"   🎯 Потенциал: €{potential_revenue:,.0f} (+€{lost_revenue:,.0f})")
                print(f"   🎧 Стримы: {row['Количество']/1e6:.1f}M")

# ============================================================================
# 5. МАТРИЦА РОСТА АРТИСТОВ (2023 vs 2024)
# ============================================================================
print("\n" + "=" * 80)
print("📊 МАТРИЦА РОСТА АРТИСТОВ")
print("=" * 80)

# Данные по годам
artists_2023 = df[df['year'] == 2023].groupby('Исполнитель').agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum'
}).reset_index()
artists_2023.columns = ['Артист', 'Выручка_2023', 'Стримы_2023']

artists_2024 = df[df['year'] == 2024].groupby('Исполнитель').agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum'
}).reset_index()
artists_2024.columns = ['Артист', 'Выручка_2024', 'Стримы_2024']

growth_matrix = pd.merge(artists_2023, artists_2024, on='Артист', how='outer').fillna(0)
growth_matrix['Рост_выручки_%'] = ((growth_matrix['Выручка_2024'] - growth_matrix['Выручка_2023']) / growth_matrix['Выручка_2023'] * 100).replace([np.inf, -np.inf], 0)
growth_matrix['Абс_рост'] = growth_matrix['Выручка_2024'] - growth_matrix['Выручка_2023']

# Категоризация
def categorize_artist(row):
    rev_2023 = row['Выручка_2023']
    rev_2024 = row['Выручка_2024']
    growth = row['Рост_выручки_%']
    
    if rev_2023 == 0 and rev_2024 > 1000:
        return '⭐ Новая звезда'
    elif rev_2024 > 10000 and growth > 50:
        return '🚀 Растущая звезда'
    elif rev_2024 > 10000 and growth > 0:
        return '💎 Стабильная звезда'
    elif rev_2024 > 5000 and growth > 100:
        return '🔥 Прорыв года'
    elif rev_2024 > 1000 and growth > 0:
        return '📈 Растущий'
    elif rev_2024 > 1000 and growth < 0:
        return '⚠️ Падающий'
    elif rev_2024 < 1000 and rev_2023 > 1000:
        return '📉 Потерянный'
    else:
        return '🌱 Начинающий'

growth_matrix['Категория'] = growth_matrix.apply(categorize_artist, axis=1)

print("\n📊 РАСПРЕДЕЛЕНИЕ АРТИСТОВ ПО КАТЕГОРИЯМ:")
category_counts = growth_matrix['Категория'].value_counts()
for cat, count in category_counts.items():
    cat_revenue = growth_matrix[growth_matrix['Категория'] == cat]['Выручка_2024'].sum()
    print(f"{cat}: {count} артистов | €{cat_revenue:,.0f} в 2024")

# Топ по категориям
for category in ['🚀 Растущая звезда', '💎 Стабильная звезда', '🔥 Прорыв года', '⭐ Новая звезда']:
    if category in growth_matrix['Категория'].values:
        print(f"\n{category}:")
        cat_artists = growth_matrix[growth_matrix['Категория'] == category].sort_values('Выручка_2024', ascending=False).head(10)
        for _, row in cat_artists.iterrows():
            if row['Выручка_2023'] > 0:
                print(f"   {row['Артист']}: €{row['Выручка_2023']:,.0f} → €{row['Выручка_2024']:,.0f} ({row['Рост_выручки_%']:+.0f}%)")
            else:
                print(f"   {row['Артист']}: NEW → €{row['Выручка_2024']:,.0f}")

# ============================================================================
# 6. МАТРИЦА ПЛАТФОРМ (РОСТ × ДОЛЯ)
# ============================================================================
print("\n" + "=" * 80)
print("📱 МАТРИЦА ПЛАТФОРМ (РОСТ × ДОЛЯ)")
print("=" * 80)

platforms_2023 = df[df['year'] == 2023].groupby('Платформа')['Сумма вознаграждения'].sum()
platforms_2024 = df[df['year'] == 2024].groupby('Платформа')['Сумма вознаграждения'].sum()

platform_matrix = pd.DataFrame({
    '2023': platforms_2023,
    '2024': platforms_2024
}).fillna(0)

platform_matrix['Рост_%'] = ((platform_matrix['2024'] - platform_matrix['2023']) / platform_matrix['2023'] * 100).replace([np.inf, -np.inf], 0)
platform_matrix['Доля_2024_%'] = (platform_matrix['2024'] / platform_matrix['2024'].sum() * 100)

# Категоризация
def categorize_platform(row):
    growth = row['Рост_%']
    share = row['Доля_2024_%']
    
    if share > 10 and growth > 20:
        return '🌟 Лидер роста'
    elif share > 10 and growth > 0:
        return '💪 Стабильный лидер'
    elif share > 10 and growth < 0:
        return '⚠️ Падающий лидер'
    elif share < 10 and growth > 50:
        return '🚀 Восходящая'
    elif share < 10 and growth > 0:
        return '📈 Растущая ниша'
    else:
        return '📉 Падающая'

platform_matrix['Категория'] = platform_matrix.apply(categorize_platform, axis=1)

print("\n📊 КАТЕГОРИИ ПЛАТФОРМ:")
for category in platform_matrix['Категория'].unique():
    print(f"\n{category}:")
    cat_platforms = platform_matrix[platform_matrix['Категория'] == category].sort_values('2024', ascending=False)
    for platform, row in cat_platforms.iterrows():
        if row['2023'] > 0:
            print(f"   {platform}: €{row['2023']:,.0f} → €{row['2024']:,.0f} ({row['Рост_%']:+.0f}%) | Доля: {row['Доля_2024_%']:.1f}%")
        else:
            print(f"   {platform}: NEW → €{row['2024']:,.0f} | Доля: {row['Доля_2024_%']:.1f}%")

# ============================================================================
# 7. ЗАВИСИМОСТЬ АРТИСТОВ ОТ ПЛАТФОРМ
# ============================================================================
print("\n" + "=" * 80)
print("🎯 ЗАВИСИМОСТЬ ТОП-АРТИСТОВ ОТ ПЛАТФОРМ")
print("=" * 80)

top_artists = df.groupby('Исполнитель')['Сумма вознаграждения'].sum().nlargest(15).index

for artist in top_artists:
    artist_data = df[df['Исполнитель'] == artist]
    platform_dist = artist_data.groupby('Платформа')['Сумма вознаграждения'].sum().sort_values(ascending=False)
    total_artist_rev = platform_dist.sum()
    
    print(f"\n{artist} (€{total_artist_rev:,.0f}):")
    for platform, rev in platform_dist.head(5).items():
        pct = (rev / total_artist_rev) * 100
        print(f"   {platform}: €{rev:,.0f} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("✅ СТРАТЕГИЧЕСКИЙ АНАЛИЗ ЗАВЕРШЕН")
print("=" * 80)

