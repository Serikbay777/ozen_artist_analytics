#!/usr/bin/env python3
"""
Скрипт для конвертации CSV файлов в SQLite базу данных
Запускается один раз для создания БД, потом можно обновлять при добавлении новых CSV
"""

import pandas as pd
import sqlite3
import os
import glob
from pathlib import Path
import sys

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_database(data_dir='data/processed', db_path='data/analytics.db', force=False):
    """
    Создаёт SQLite базу данных из CSV файлов
    
    Args:
        data_dir: Папка с CSV файлами
        db_path: Путь к SQLite базе
        force: Пересоздать БД даже если она существует
    """
    
    # Проверяем существование БД
    if os.path.exists(db_path) and not force:
        print(f"⚠️  База данных уже существует: {db_path}")
        print(f"   Используйте --force для пересоздания")
        return
    
    # Удаляем старую БД если force=True
    if os.path.exists(db_path) and force:
        os.remove(db_path)
        print(f"🗑️  Удалена старая база данных")
    
    # Находим все CSV файлы
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not csv_files:
        print(f"❌ CSV файлы не найдены в {data_dir}")
        return
    
    print(f"📁 Найдено {len(csv_files)} CSV файлов")
    print(f"🎯 Создаём базу данных: {db_path}")
    print()
    
    # Создаём подключение к БД
    conn = sqlite3.connect(db_path)
    
    # Оптимизированные типы данных для экономии места
    dtypes = {
        'Исполнитель': 'category',
        'Название трека': 'category',
        'Платформа': 'category',
        'страна / регион': 'category',
        'Лейбл': 'category',
        'Тип продажи': 'category',
        'Тип релиза': 'category',
        'Название релиза': 'category'
    }
    
    # Колонки которые нам нужны
    usecols = [
        'Месяц отчета',
        'Исполнитель',
        'Название трека',
        'Платформа',
        'Сумма вознаграждения',
        'Количество',
        'страна / регион',
        'Лейбл',
        'Тип продажи'
    ]
    
    total_rows = 0
    
    # Загружаем каждый CSV файл
    for csv_file in csv_files:
        print(f"📊 Обработка: {os.path.basename(csv_file)}")
        
        try:
            # Читаем CSV с оптимизацией
            df = pd.read_csv(
                csv_file,
                sep=';',
                usecols=lambda x: x in usecols,
                dtype=dtypes,
                low_memory=False
            )
            
            # Конвертируем дату
            df['Месяц отчета'] = pd.to_datetime(df['Месяц отчета'], errors='coerce')
            
            # Добавляем производные колонки
            df['year'] = df['Месяц отчета'].dt.year
            df['month'] = df['Месяц отчета'].dt.month
            df['quarter'] = df['Месяц отчета'].dt.quarter
            
            # Сохраняем в SQLite
            df.to_sql(
                'analytics',
                conn,
                if_exists='append',
                index=False,
                chunksize=10000  # Загружаем по частям для экономии памяти
            )
            
            total_rows += len(df)
            print(f"   ✓ Загружено {len(df):,} строк")
            
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
    
    print()
    print(f"📊 Всего загружено: {total_rows:,} строк")
    print()
    print("🔧 Создание индексов для ускорения запросов...")
    
    # Создаём индексы для быстрых запросов
    indexes = [
        ("idx_artist", "Исполнитель"),
        ("idx_track", "Название трека"),
        ("idx_platform", "Платформа"),
        ("idx_country", "страна / регион"),
        ("idx_date", "Месяц отчета"),
        ("idx_year", "year"),
        ("idx_label", "Лейбл"),
    ]
    
    for idx_name, column in indexes:
        try:
            conn.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON analytics("{column}")')
            print(f"   ✓ Создан индекс: {idx_name}")
        except Exception as e:
            print(f"   ⚠️  Индекс {idx_name}: {e}")
    
    # Создаём составные индексы для сложных запросов
    try:
        conn.execute('CREATE INDEX IF NOT EXISTS idx_artist_track ON analytics("Исполнитель", "Название трека")')
        print(f"   ✓ Создан индекс: idx_artist_track")
    except:
        pass
    
    conn.commit()
    
    # Получаем размер БД
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    
    print()
    print("=" * 60)
    print("✅ База данных успешно создана!")
    print(f"📁 Путь: {db_path}")
    print(f"💾 Размер: {db_size:.1f} MB")
    print(f"📊 Строк: {total_rows:,}")
    print("=" * 60)
    
    conn.close()


def update_database(data_dir='data/processed', db_path='data/analytics.db'):
    """
    Обновляет базу данных новыми CSV файлами
    (Пока простая версия - пересоздаёт БД)
    """
    print("🔄 Обновление базы данных...")
    create_database(data_dir, db_path, force=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Конвертация CSV в SQLite')
    parser.add_argument('--data-dir', default='data/processed', help='Папка с CSV файлами')
    parser.add_argument('--db-path', default='data/analytics.db', help='Путь к SQLite базе')
    parser.add_argument('--force', action='store_true', help='Пересоздать БД')
    parser.add_argument('--update', action='store_true', help='Обновить БД')
    
    args = parser.parse_args()
    
    if args.update:
        update_database(args.data_dir, args.db_path)
    else:
        create_database(args.data_dir, args.db_path, args.force)

