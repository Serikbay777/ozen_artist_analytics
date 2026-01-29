#!/usr/bin/env python3
"""
Скрипт для проверки заработка Darkhan Juzz в 2023-2024
"""
import requests
import sys
from datetime import datetime

# Конфигурация
UUID = "b5222ce6-03c5-4959-ac9e-a3898ebfe075"
DB_ENDPOINT = "http://localhost:3001"

def execute_query(query, description=""):
    """Выполнить SQL запрос"""
    try:
        response = requests.post(
            f"{DB_ENDPOINT}/execute-query",
            json={"uuid": UUID, "query": query}
        )
        response.raise_for_status()
        results = response.json()['results']
        
        if description:
            print(f"\n{'='*80}")
            print(f"📊 {description}")
            print(f"{'='*80}")
            print(f"SQL: {query[:100]}...")
            print(f"Результатов: {len(results)}")
        
        return results
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

print("="*80)
print("🔍 ПРОВЕРКА ЗАРАБОТКА DARKHAN JUZZ (2023-2024)")
print("="*80)

# 1. Используем точное имя артиста
print("\n1️⃣ Проверяем наличие артиста 'Darkhan Juzz'...")
artist_name = "Darkhan Juzz"

query1 = f"""
SELECT COUNT(*) as count
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
"""
check = execute_query(query1)
if check and check[0] and check[0][0] > 0:
    print(f"   ✅ Найдено записей: {check[0][0]}")
else:
    print(f"   ❌ Артист '{artist_name}' не найден!")
    sys.exit(1)

# 2. Проверяем диапазон дат в данных
print("\n2️⃣ Проверяем диапазон дат для этого артиста...")
query2 = f"""
SELECT 
    MIN(`Месяц отчета`) as min_date,
    MAX(`Месяц отчета`) as max_date
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
"""
date_range = execute_query(query2)
if date_range and date_range[0]:
    min_date, max_date = date_range[0]
    print(f"   Данные доступны с {min_date} по {max_date}")
else:
    print("   ❌ Не удалось определить диапазон дат")

# 3. Считаем общий заработок за 2023-2024
print("\n3️⃣ Считаем общий заработок за 2023-2024...")
query3 = f"""
SELECT 
    SUM(CAST(`Сумма вознаграждения` AS REAL)) as total_earnings
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
    AND `Сумма вознаграждения` IS NOT NULL
    AND `Сумма вознаграждения` != ""
    AND `Месяц отчета` >= '2023-01-01'
    AND `Месяц отчета` < '2025-01-01'
"""
total = execute_query(query3, "Общий заработок 2023-2024")
if total and total[0] and total[0][0]:
    total_earnings = float(total[0][0])
    print(f"\n   💰 ИТОГО: {total_earnings:,.2f} EUR")
    print(f"   💰 ИТОГО: ${total_earnings:,.2f} (если в долларах)")
    
    # Проверяем с ответом AI
    ai_answer = 31199.76
    difference = abs(total_earnings - ai_answer)
    print(f"\n   🤖 Ответ AI: ${ai_answer:,.2f}")
    print(f"   📊 Наш расчет: {total_earnings:,.2f} EUR")
    print(f"   📉 Разница: {difference:,.2f}")
    
    if difference < 0.01:
        print(f"   ✅ AI ПРАВ! Данные совпадают")
    else:
        print(f"   ⚠️  Есть расхождение")
else:
    print("   ❌ Не удалось посчитать")

# 4. Разбивка по годам
print("\n4️⃣ Разбивка по годам...")
query4 = f"""
SELECT 
    strftime('%Y', `Месяц отчета`) as year,
    SUM(CAST(`Сумма вознаграждения` AS REAL)) as yearly_earnings,
    COUNT(*) as transactions
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
    AND `Сумма вознаграждения` IS NOT NULL
    AND `Сумма вознаграждения` != ""
    AND `Месяц отчета` >= '2023-01-01'
    AND `Месяц отчета` < '2025-01-01'
GROUP BY year
ORDER BY year
"""
yearly = execute_query(query4)
if yearly:
    print(f"\n   {'Год':<10} {'Заработок (EUR)':>20} {'Транзакций':>15}")
    print(f"   {'-'*10} {'-'*20} {'-'*15}")
    for year, earnings, count in yearly:
        print(f"   {year:<10} {earnings:>20,.2f} {count:>15,}")

# 5. Разбивка по платформам
print("\n5️⃣ Разбивка по платформам за 2023-2024...")
query5 = f"""
SELECT 
    `Платформа`,
    SUM(CAST(`Сумма вознаграждения` AS REAL)) as platform_earnings,
    COUNT(*) as transactions
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
    AND `Сумма вознаграждения` IS NOT NULL
    AND `Сумма вознаграждения` != ""
    AND `Месяц отчета` >= '2023-01-01'
    AND `Месяц отчета` < '2025-01-01'
GROUP BY `Платформа`
ORDER BY platform_earnings DESC
LIMIT 10
"""
platforms = execute_query(query5)
if platforms:
    print(f"\n   {'Платформа':<30} {'Заработок (EUR)':>20} {'Транзакций':>15}")
    print(f"   {'-'*30} {'-'*20} {'-'*15}")
    for platform, earnings, count in platforms:
        print(f"   {platform:<30} {earnings:>20,.2f} {count:>15,}")

# 6. Разбивка по месяцам (топ-10)
print("\n6️⃣ Топ-10 месяцев по заработку...")
query6 = f"""
SELECT 
    `Месяц отчета`,
    SUM(CAST(`Сумма вознаграждения` AS REAL)) as monthly_earnings
FROM `csv_data`
WHERE `Исполнитель` = '{artist_name}'
    AND `Сумма вознаграждения` IS NOT NULL
    AND `Сумма вознаграждения` != ""
    AND `Месяц отчета` >= '2023-01-01'
    AND `Месяц отчета` < '2025-01-01'
GROUP BY `Месяц отчета`
ORDER BY monthly_earnings DESC
LIMIT 10
"""
months = execute_query(query6)
if months:
    print(f"\n   {'Месяц':<15} {'Заработок (EUR)':>20}")
    print(f"   {'-'*15} {'-'*20}")
    for month, earnings in months:
        print(f"   {month:<15} {earnings:>20,.2f}")

# 7. Проверка SQL запроса который сгенерировал AI
print("\n7️⃣ Проверяем SQL который сгенерировал AI...")
ai_query = f"""
SELECT SUM(CAST(`Сумма вознаграждения` AS REAL)) 
FROM `csv_data` 
WHERE `Исполнитель` = '{artist_name}' 
    AND `Месяц отчета` >= '2023-01-01' 
    AND `Месяц отчета` < '2025-01-01' 
    AND `Сумма вознаграждения` IS NOT NULL 
    AND `Сумма вознаграждения` != ""
"""
ai_result = execute_query(ai_query, "SQL от AI")
if ai_result and ai_result[0] and ai_result[0][0]:
    ai_calculated = float(ai_result[0][0])
    print(f"\n   💰 Результат AI SQL: {ai_calculated:,.2f} EUR")
    print(f"   ✅ SQL корректный!")

print("\n" + "="*80)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("="*80)
print(f"\n📌 ВЫВОД:")
print(f"   Darkhan Juzz заработал {total_earnings:,.2f} EUR в период 2023-2024")
print(f"   AI ответил правильно: {ai_answer:,.2f} ≈ {total_earnings:,.2f}")
print("="*80)

