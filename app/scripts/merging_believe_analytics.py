"""
Объединяет все CSV отчеты от Believe в один файл
"""

import pandas as pd
import glob
import os
import sys

# Добавляем корневую папку проекта в path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

print("🚀 Объединение CSV файлов Believe")
print("=" * 60)

# Пути относительно корня проекта
data_dir = '/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/data'
output_dir = '/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/data/processed'

# Создаем папку для результатов если нет
os.makedirs(output_dir, exist_ok=True)

print(f"📁 Папка с данными: {data_dir}")
print(f"📁 Папка для результатов: {output_dir}")

# Ищем все CSV файлы (в папке data и подпапках)
csv_pattern = os.path.join(data_dir, '**', '*.csv')
csv_files = glob.glob(csv_pattern, recursive=True)

# Исключаем папку processed
csv_files = [f for f in csv_files if 'processed' not in f]

if len(csv_files) == 0:
    print("\n❌ CSV файлы не найдены!")
    print(f"   Проверьте путь: {data_dir}")
    print(f"   Положите CSV файлы в: music_analyzer/data/")
    sys.exit(1)

print(f"\n✅ Найдено {len(csv_files)} файлов:")
for file in csv_files:
    size_kb = os.path.getsize(file) / 1024
    rel_path = os.path.relpath(file, project_root)
    print(f"   - {rel_path} ({size_kb:.1f} KB)")

print("\n" + "=" * 60)
print("📖 Читаю файлы...")

# Читаем все CSV
all_dataframes = []
errors = []

for i, file in enumerate(csv_files, 1):
    filename = os.path.basename(file)
    print(f"   [{i}/{len(csv_files)}] {filename}...", end=' ')
    
    try:
        # Пробуем разные варианты чтения
        try:
            df = pd.read_csv(file, sep=';', encoding='utf-8')
        except:
            try:
                df = pd.read_csv(file, sep=',', encoding='utf-8')
            except:
                df = pd.read_csv(file, sep=';', encoding='latin1')
        
        # Добавляем метаданные
        df['source_file'] = filename
        
        all_dataframes.append(df)
        print(f"✅ ({len(df):,} строк)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        errors.append({'file': filename, 'error': str(e)})

if len(all_dataframes) == 0:
    print("\n❌ Не удалось загрузить ни одного файла!")
    sys.exit(1)

# Объединяем все
print("\n" + "=" * 60)
print("🔗 Объединяю данные...")

merged = pd.concat(all_dataframes, ignore_index=True)
print(f"✅ Объединено: {len(merged):,} строк × {len(merged.columns)} колонок")

# Чистим данные
print("\n🧹 Чищу данные...")

# Конвертируем числовые поля
numeric_cols = [
    'Общий доход', 
    'Сумма вознаграждения', 
    'Количество', 
    'Цена за единицу',
    'Авторские отчисления (механика)',
    'Ставка вознаграждения'
]

for col in numeric_cols:
    if col in merged.columns:
        merged[col] = pd.to_numeric(
            merged[col].astype(str).str.replace(',', '.'),
            errors='coerce'
        )

# Конвертируем даты
date_cols = ['Месяц отчета', 'Месяц продажи']
for col in date_cols:
    if col in merged.columns:
        merged[col] = pd.to_datetime(merged[col], errors='coerce')

print("✅ Данные очищены")

# Статистика
print("\n" + "=" * 60)
print("📊 СТАТИСТИКА")
print("=" * 60)

if 'Месяц отчета' in merged.columns:
    min_date = merged['Месяц отчета'].min()
    max_date = merged['Месяц отчета'].max()
    print(f"\n📅 Период данных:")
    print(f"   От: {min_date}")
    print(f"   До: {max_date}")

if 'Сумма вознаграждения' in merged.columns:
    total_revenue = merged['Сумма вознаграждения'].sum()
    currency = merged['Валюта'].iloc[0] if 'Валюта' in merged.columns else 'EUR'
    print(f"\n💰 Выручка:")
    print(f"   Всего: {currency}{total_revenue:,.2f}")

if 'Количество' in merged.columns:
    total_streams = merged['Количество'].sum()
    print(f"\n🎵 Стримы:")
    print(f"   Всего: {total_streams:,.0f}")

if 'Исполнитель' in merged.columns:
    print(f"\n🎤 Контент:")
    print(f"   Артистов: {merged['Исполнитель'].nunique()}")
    
if 'Название трека' in merged.columns:
    print(f"   Треков: {merged['Название трека'].nunique()}")

if 'Платформа' in merged.columns:
    print(f"   Платформ: {merged['Платформа'].nunique()}")

if 'страна / регион' in merged.columns:
    print(f"   Стран: {merged['страна / регион'].nunique()}")

# Топ-5 артистов
if 'Исполнитель' in merged.columns and 'Сумма вознаграждения' in merged.columns:
    print(f"\n🏆 Топ-5 артистов:")
    top = merged.groupby('Исполнитель')['Сумма вознаграждения'].sum().sort_values(ascending=False).head(5)
    for artist, revenue in top.items():
        print(f"   {artist}: {currency}{revenue:,.2f}")

# Сохраняем
print("\n" + "=" * 60)
print("💾 Сохраняю результаты...")

# CSV
csv_path = os.path.join(output_dir, 'all_believe_data.csv')
merged.to_csv(csv_path, index=False, encoding='utf-8')
csv_size_mb = os.path.getsize(csv_path) / 1024 / 1024
print(f"   ✅ CSV: {csv_size_mb:.1f} MB")

# Pickle (быстрая загрузка)
pkl_path = os.path.join(output_dir, 'all_believe_data.pkl')
merged.to_pickle(pkl_path)
pkl_size_mb = os.path.getsize(pkl_path) / 1024 / 1024
print(f"   ✅ Pickle: {pkl_size_mb:.1f} MB")

# Parquet (сжатый)
try:
    parquet_path = os.path.join(output_dir, 'all_believe_data.parquet')
    merged.to_parquet(parquet_path, index=False)
    parquet_size_mb = os.path.getsize(parquet_path) / 1024 / 1024
    print(f"   ✅ Parquet: {parquet_size_mb:.1f} MB")
except:
    print(f"   ⚠️  Parquet: не установлен pyarrow")

# Summary файл
summary_path = os.path.join(output_dir, 'data_summary.txt')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("BELIEVE ANALYTICS - DATA SUMMARY\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Файлов обработано: {len(csv_files)}\n")
    f.write(f"Всего строк: {len(merged):,}\n")
    f.write(f"Колонок: {len(merged.columns)}\n\n")
    
    f.write("КОЛОНКИ:\n")
    for col in merged.columns:
        f.write(f"  - {col}\n")
    
    if errors:
        f.write(f"\n\nОШИБКИ ({len(errors)}):\n")
        for error in errors:
            f.write(f"  - {error['file']}: {error['error']}\n")

print(f"   ✅ Summary: data_summary.txt")

# Финал
print("\n" + "=" * 60)
print("🎉 ГОТОВО!")
print("=" * 60)
print("\nВаши данные сохранены в:")
print(f"   📁 {os.path.relpath(output_dir, project_root)}/")
print(f"      - all_believe_data.csv")
print(f"      - all_believe_data.pkl")
print(f"      - all_believe_data.parquet")
print(f"      - data_summary.txt")

print("\n💡 Как использовать в Python:")
print("   import pandas as pd")
print(f"   df = pd.read_pickle('{os.path.join('app', 'data', 'processed', 'all_believe_data.pkl')}')")
print("   print(df.head())")

if errors:
    print(f"\n⚠️  Внимание: {len(errors)} файлов с ошибками (см. data_summary.txt)")

print("\n✨ Готово к анализу! 🚀\n")