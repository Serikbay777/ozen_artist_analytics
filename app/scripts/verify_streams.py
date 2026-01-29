#!/usr/bin/env python3
"""
Скрипт для проверки количества стримов у треков Darkhan Juzz
"""
import requests
import json

# UUID вашей базы данных
UUID = "b5222ce6-03c5-4959-ac9e-a3898ebfe075"
DB_ENDPOINT = "http://localhost:3001"

def execute_query(query):
    """Выполнить SQL запрос"""
    try:
        response = requests.post(
            f"{DB_ENDPOINT}/execute-query",
            json={"uuid": UUID, "query": query}
        )
        response.raise_for_status()
        return response.json()['results']
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

print("=" * 80)
print("🔍 ПРОВЕРКА ДАННЫХ ПО DARKHAN JUZZ")
print("=" * 80)

# 1. Найти все треки Darkhan Juzz
print("\n1️⃣ Ищем все треки исполнителя Darkhan Juzz...")
query1 = """
SELECT DISTINCT `Название трека`
FROM `csv_data`
WHERE `Исполнитель` LIKE '%Darkhan%'
"""
tracks = execute_query(query1)
if tracks:
    print(f"   Найдено треков: {len(tracks)}")
    for i, track in enumerate(tracks, 1):
        print(f"   {i}. {track[0]}")
else:
    print("   ❌ Треки не найдены")

# 2. Подсчитать стримы для каждого трека
print("\n2️⃣ Подсчитываем стримы для каждого трека...")
query2 = """
SELECT 
    `Название трека`, 
    SUM(CAST(`Количество` AS REAL)) as total_streams
FROM `csv_data`
WHERE `Исполнитель` LIKE '%Darkhan%'
    AND `Количество` IS NOT NULL 
    AND `Количество` != ""
GROUP BY `Название трека`
ORDER BY total_streams DESC
"""
results = execute_query(query2)
if results:
    print(f"\n   📊 Результаты:")
    print(f"   {'Трек':<40} {'Стримы':>15}")
    print(f"   {'-'*40} {'-'*15}")
    for track_name, streams in results:
        print(f"   {track_name:<40} {streams:>15,.0f}")
else:
    print("   ❌ Данные не найдены")

# 3. Проверить конкретные треки из ответа LLM
print("\n3️⃣ Проверяем конкретные треки из ответа LLM...")
tracks_to_check = ["Úıde", "Sheker"]

for track in tracks_to_check:
    query3 = f"""
    SELECT 
        `Название трека`,
        SUM(CAST(`Количество` AS REAL)) as total_streams
    FROM `csv_data`
    WHERE `Исполнитель` LIKE '%Darkhan%'
        AND `Название трека` = '{track}'
        AND `Количество` IS NOT NULL 
        AND `Количество` != ""
    GROUP BY `Название трека`
    """
    result = execute_query(query3)
    if result and len(result) > 0:
        track_name, streams = result[0]
        print(f"   ✓ {track_name}: {streams:,.0f} стримов")
    else:
        print(f"   ❌ {track}: не найдено")

# 4. Проверить точное написание исполнителя
print("\n4️⃣ Проверяем точное написание исполнителя...")
query4 = """
SELECT DISTINCT `Исполнитель`
FROM `csv_data`
WHERE `Исполнитель` LIKE '%Darkhan%'
"""
artists = execute_query(query4)
if artists:
    print(f"   Найдено вариантов написания: {len(artists)}")
    for artist in artists:
        print(f"   - {artist[0]}")

print("\n" + "=" * 80)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)

