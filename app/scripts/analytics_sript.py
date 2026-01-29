import pandas as pd
import matplotlib.pyplot as plt

# Загрузить
df = pd.read_pickle('/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/data/processed/all_believe_data.pkl')

print("=" * 60)
print("📊 DEEPER ANALYSIS")
print("=" * 60)

# 1. ПО ГОДАМ
df['year'] = df['Месяц отчета'].dt.year
yearly = df.groupby('year').agg({
    'Сумма вознаграждения': 'sum',
    'Количество': 'sum',
    'Исполнитель': 'nunique'
})

print("\n📅 ДИНАМИКА ПО ГОДАМ:")
print(yearly)

# Рост year-over-year
print("\n📈 РОСТ:")
for year in range(2021, 2025):
    if year in yearly.index:
        rev = yearly.loc[year, 'Сумма вознаграждения']
        streams = yearly.loc[year, 'Количество']
        artists = yearly.loc[year, 'Исполнитель']
        
        if year > 2021 and year-1 in yearly.index:
            prev_rev = yearly.loc[year-1, 'Сумма вознаграждения']
            growth = ((rev - prev_rev) / prev_rev) * 100
            print(f"{year}: €{rev:,.0f} ({growth:+.1f}% YoY) | {streams/1e6:.1f}M стримов | {artists} артистов")
        else:
            print(f"{year}: €{rev:,.0f} | {streams/1e6:.1f}M стримов | {artists} артистов")

# 2. КОНЦЕНТРАЦИЯ ДОХОДОВ
print("\n💰 КОНЦЕНТРАЦИЯ:")
top_10_rev = df.groupby('Исполнитель')['Сумма вознаграждения'].sum().sort_values(ascending=False).head(10).sum()
top_20_rev = df.groupby('Исполнитель')['Сумма вознаграждения'].sum().sort_values(ascending=False).head(20).sum()
top_50_rev = df.groupby('Исполнитель')['Сумма вознаграждения'].sum().sort_values(ascending=False).head(50).sum()
total_rev = df['Сумма вознаграждения'].sum()

print(f"Топ-10 артистов: €{top_10_rev:,.0f} ({top_10_rev/total_rev*100:.1f}%)")
print(f"Топ-20 артистов: €{top_20_rev:,.0f} ({top_20_rev/total_rev*100:.1f}%)")
print(f"Топ-50 артистов: €{top_50_rev:,.0f} ({top_50_rev/total_rev*100:.1f}%)")

# 3. ПЛАТФОРМЫ
print("\n📱 ТОП-10 ПЛАТФОРМ:")
platforms = df.groupby('Платформа')['Сумма вознаграждения'].sum().sort_values(ascending=False).head(10)
for platform, rev in platforms.items():
    pct = (rev / total_rev) * 100
    print(f"   {platform}: €{rev:,.0f} ({pct:.1f}%)")

# 4. ГЕОГРАФИЯ
print("\n🌍 ТОП-10 СТРАН:")
countries = df.groupby('страна / регион')['Количество'].sum().sort_values(ascending=False).head(10)
total_streams = df['Количество'].sum()
for country, streams in countries.items():
    pct = (streams / total_streams) * 100
    print(f"   {country}: {streams/1e6:.1f}M стримов ({pct:.1f}%)")

# 5. CPM АНАЛИЗ
print("\n💵 CPM ПО ПЛАТФОРМАМ (топ-10):")
platform_cpm = df.groupby('Платформа').apply(
    lambda x: (x['Сумма вознаграждения'].sum() / x['Количество'].sum() * 1000) if x['Количество'].sum() > 0 else 0
).sort_values(ascending=False).head(10)
for platform, cpm in platform_cpm.items():
    print(f"   {platform}: €{cpm:.3f} за 1000 стримов")

print("\n" + "=" * 60)