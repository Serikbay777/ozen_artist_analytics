#!/usr/bin/env python3
"""
PDF Report Generator for Mona Songz - Quarterly Payments Report
With Cyrillic font support
"""

import json
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io

# КРИТИЧНО: Регистрация шрифтов с поддержкой кириллицы
try:
    # Попытка 1: Системный шрифт macOS с кириллицей
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
    print("✓ Загружены шрифты с поддержкой кириллицы (Arial Unicode)")
except:
    try:
        # Попытка 2: DejaVu Sans (если установлен)
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/Library/Fonts/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/Library/Fonts/DejaVuSans-Bold.ttf'))
        FONT_NAME = 'DejaVuSans'
        FONT_NAME_BOLD = 'DejaVuSans-Bold'
        print("✓ Загружены шрифты DejaVu Sans")
    except:
        try:
            # Попытка 3: Arial (если есть)
            pdfmetrics.registerFont(TTFont('DejaVuSans', '/Library/Fonts/Arial.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/Library/Fonts/Arial Bold.ttf'))
            FONT_NAME = 'DejaVuSans'
            FONT_NAME_BOLD = 'DejaVuSans-Bold'
            print("✓ Загружены шрифты Arial")
        except:
            print("⚠ ВНИМАНИЕ: Не удалось загрузить шрифты с кириллицей!")
            print("Установите DejaVu Sans: brew install --cask font-dejavu")
            FONT_NAME = 'Helvetica'
            FONT_NAME_BOLD = 'Helvetica-Bold'

# Настройка matplotlib для кириллицы
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Arial']

# Paths
JSON_PATH = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/Mona_Songz_quarter_report.json"
MEDIALAND_SUMMARY = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_summary_medialand.csv"
MEDIALAND_MONTHLY = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_monthly_medialand.csv"
MEDIALAND_PLATFORMS = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_platforms_medialand.csv"
MEDIALAND_COUNTRIES = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_countries_medialand.csv"
MEDIALAND_TRACKS = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_tracks_medialand.csv"
OUTPUT_PATH = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/Mona_Songz_Quarter_Report_Q4_2025.pdf"


def load_json_data():
    """Load main JSON report data"""
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_data(path):
    """Load CSV data"""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def create_chart_revenue_by_month(data):
    """Create revenue by month chart - Q4 2025 + Остальные"""
    months = []
    revenues = []
    
    # Q4 2025: последние 3 месяца
    q4_months = data['time_series']['by_sales_month'][-3:]
    other_months = data['time_series']['by_sales_month'][:-3]
    
    # Добавляем Q4
    for item in q4_months:
        month = item['month'].split('/')[1]
        year = item['month'].split('/')[0][-2:]  # последние 2 цифры года
        months.append(f"{month}/{year}")
        revenues.append(item['revenue'])
    
    # Добавляем "Остальные"
    if other_months:
        total_other_revenue = sum(item['revenue'] for item in other_months)
        months.append('Остальные')
        revenues.append(total_other_revenue)
    
    # Разные цвета для Q4 и остальных
    colors_list = ['#4CAF50', '#4CAF50', '#4CAF50', '#95a5a6']  # зеленый для Q4, серый для остальных
    
    plt.figure(figsize=(8, 4))
    plt.bar(months, revenues, color=colors_list[:len(months)], alpha=0.8)
    plt.xlabel('Период', fontsize=10)
    plt.ylabel('Доход (EUR)', fontsize=10)
    plt.title('Доход по периодам (Q4 2025 + Остальные)', fontsize=12, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close()
    
    return buf


def create_chart_platforms(data):
    """Create top platforms pie chart"""
    platforms = []
    revenues = []
    
    top_platforms = sorted(data['platforms']['platforms'], 
                          key=lambda x: x['revenue'], reverse=True)[:5]
    
    for p in top_platforms:
        platforms.append(p['platform'][:15])  # Truncate long names
        revenues.append(p['revenue'])
    
    plt.figure(figsize=(7, 5))
    colors_list = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    plt.pie(revenues, labels=platforms, autopct='%1.1f%%', 
            colors=colors_list, startangle=90)
    plt.title('Топ-5 платформ по доходу', fontsize=12, fontweight='bold')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close()
    
    return buf


def create_chart_countries(data):
    """Create top countries bar chart"""
    countries = []
    revenues = []
    
    for country in data['geography']['top_countries'][:8]:
        countries.append(country['country'][:15])
        revenues.append(country['revenue'])
    
    plt.figure(figsize=(8, 5))
    plt.barh(countries, revenues, color='#5C6BC0', alpha=0.8)
    plt.xlabel('Доход (EUR)', fontsize=10)
    plt.title('Топ-8 стран по доходу', fontsize=12, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close()
    
    return buf


def format_number(num):
    """Format number with thousand separators"""
    if isinstance(num, (int, float)):
        return f"{num:,.0f}".replace(',', ' ')
    return str(num)


def format_currency(amount, currency='EUR'):
    """Format currency"""
    if isinstance(amount, (int, float)):
        if currency == 'EUR':
            return f"€{amount:,.2f}".replace(',', ' ')
        elif currency == 'KZT':
            return f"{amount:,.0f} ₸".replace(',', ' ')
    return str(amount)


class PDFReport:
    def __init__(self):
        self.doc = SimpleDocTemplate(
            OUTPUT_PATH,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.width = A4[0] - 40*mm
        
        # Custom styles с кириллическими шрифтами
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME_BOLD,
            fontSize=24,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontName=FONT_NAME_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=10,
            spaceBefore=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontName=FONT_NAME_BOLD,
            fontSize=12,
            textColor=colors.HexColor('#5C6BC0'),
            spaceAfter=8,
            spaceBefore=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#424242')
        ))
    
    def add_header(self, data):
        """Add report header with company info"""
        # Title
        title = Paragraph("КВАРТАЛЬНЫЙ ОТЧЁТ", self.styles['CustomTitle'])
        self.story.append(title)
        
        subtitle = Paragraph(
            f"<b>Артист:</b> {data['artist_name']}<br/>"
            f"<b>Период:</b> Q4 2025 ({data['period']['start']} - {data['period']['end']})<br/>"
            f"<b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y')}",
            self.styles['ContactInfo']
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 10*mm))
        
        # Company contact info
        contact_info = Paragraph(
            "<b>БИН</b> 190440002324 | <b>ИИК</b> KZ5096503F0008550902 | <b>БИК</b> IRTYKZKA<br/>"
            '<b>АО "ForteBank"</b> г. Астана<br/>'
            "<b>E-mail:</b> ozenxo@gmail.com | <b>Адрес:</b> г. Астана, ул. Е-755, д. 1, офис 127",
            self.styles['ContactInfo']
        )
        self.story.append(contact_info)
        self.story.append(Spacer(1, 10*mm))
        
        # Separator line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[self.width])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#2E3192'))
        ]))
        self.story.append(line_table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_kpi_summary(self, data):
        """Add KPI summary section"""
        heading = Paragraph("КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        kpi_data = [
            ['Показатель', 'Значение'],
            ['Общие стримы', format_number(data['overview']['total_streams'])],
            ['Общий доход (Believe)', format_currency(data['overview']['total_revenue'])],
            ['Заработок артиста (74.8%)', format_currency(data['overview']['artist_earnings'])],
            ['Уникальных треков', str(data['overview']['unique_tracks'])],
            ['Уникальных релизов', str(data['overview']['unique_releases'])],
            ['Охват стран', str(data['overview']['unique_countries'])],
            ['Количество платформ', str(data['overview']['unique_platforms'])],
            ['Средняя цена за стрим', format_currency(data['financial']['avg_price_per_stream'])],
        ]
        
        table = Table(kpi_data, colWidths=[self.width * 0.6, self.width * 0.4])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_medialand_summary(self):
        """Add Medialand summary section"""
        heading = Paragraph("ДАННЫЕ МЕДИАЛЭНД (Авторские отчисления)", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        try:
            medialand_data = load_csv_data(MEDIALAND_SUMMARY)
            if medialand_data:
                summary = medialand_data[0]
                
                data = [
                    ['Показатель', 'Значение'],
                    ['Общие стримы (Medialand)', summary.get('Total Streams', 'N/A')],
                    ['Доход в тенге', summary.get('Total Revenue (KZT)', 'N/A')],
                    ['Доход в евро', summary.get('Total Revenue (EUR)', 'N/A')],
                    ['Уникальных треков', summary.get('Unique Tracks', 'N/A')],
                    ['Платформ', summary.get('Unique Platforms', 'N/A')],
                    ['Стран', summary.get('Unique Countries', 'N/A')],
                    ['Средняя цена за стрим (₸)', summary.get('Avg Price per Stream (KZT)', 'N/A')],
                ]
                
                table = Table(data, colWidths=[self.width * 0.6, self.width * 0.4])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
                    ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                self.story.append(table)
                self.story.append(Spacer(1, 8*mm))
        except Exception as e:
            print(f"Ошибка загрузки данных Medialand: {e}")
    
    def add_top_tracks(self, data):
        """Add top tracks section"""
        heading = Paragraph("ТОП ТРЕКИ", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        tracks_data = [['Трек', 'Стримы', 'Доход (EUR)', '% от дохода']]
        
        for track in data['tracks']['tracks']:
            tracks_data.append([
                track['track_name'][:30],
                format_number(track['streams']),
                format_currency(track['revenue']),
                f"{track['revenue'] / data['overview']['total_revenue'] * 100:.1f}%"
            ])
        
        table = Table(tracks_data, colWidths=[
            self.width * 0.4,
            self.width * 0.2,
            self.width * 0.2,
            self.width * 0.2
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_platforms_analysis(self, data):
        """Add platforms analysis"""
        heading = Paragraph("АНАЛИЗ ПЛАТФОРМ (Топ-10)", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        platforms_data = [['Платформа', 'Стримы', 'Доход', '€/стрим']]
        
        top_platforms = sorted(data['platforms']['platforms'], 
                              key=lambda x: x['revenue'], reverse=True)[:10]
        
        for p in top_platforms:
            platforms_data.append([
                p['platform'][:25],
                format_number(p['streams']),
                format_currency(p['revenue']),
                f"€{p['avg_price_per_stream']:.4f}"
            ])
        
        table = Table(platforms_data, colWidths=[
            self.width * 0.4,
            self.width * 0.2,
            self.width * 0.2,
            self.width * 0.2
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 5*mm))
    
    def add_countries_analysis(self, data):
        """Add countries analysis"""
        heading = Paragraph("ГЕОГРАФИЯ (Топ-12 стран)", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        countries_data = [['Страна', 'Стримы', 'Доход (EUR)', '% стримов']]
        
        for country in data['geography']['top_countries'][:12]:
            countries_data.append([
                country['country'][:20],
                format_number(country['streams']),
                format_currency(country['revenue']),
                f"{country['percentage']:.1f}%"
            ])
        
        table = Table(countries_data, colWidths=[
            self.width * 0.35,
            self.width * 0.25,
            self.width * 0.2,
            self.width * 0.2
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_monthly_dynamics(self, data):
        """Add monthly dynamics - Q4 2025 + Остальные"""
        heading = Paragraph("ДИНАМИКА ПО МЕСЯЦАМ", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        # Словарь для русских названий месяцев
        months_ru = {
            'January': 'Январь', 'February': 'Февраль', 'March': 'Март',
            'April': 'Апрель', 'May': 'Май', 'June': 'Июнь',
            'July': 'Июль', 'August': 'Август', 'September': 'Сентябрь',
            'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'
        }
        
        monthly_data = [['Месяц', 'Стримы', 'Доход (EUR)', 'Рост стримов', 'Рост дохода']]
        
        # Q4 2025: последние 3 месяца (октябрь, ноябрь, декабрь 2025)
        q4_months = data['time_series']['by_sales_month'][-3:]
        other_months = data['time_series']['by_sales_month'][:-3]
        
        # Добавляем Q4 2025
        for item in q4_months:
            month_obj = datetime.strptime(item['month'], '%Y/%m/%d')
            month_eng = month_obj.strftime('%B')
            month_str = f"{months_ru.get(month_eng, month_eng)} {month_obj.year}"
            streams_growth = item.get('streams_growth', 0)
            revenue_growth = item.get('revenue_growth', 0)
            
            monthly_data.append([
                month_str,
                format_number(item['streams']),
                format_currency(item['revenue']),
                f"{streams_growth:.1f}%" if streams_growth else '-',
                f"{revenue_growth:.1f}%" if revenue_growth else '-'
            ])
        
        # Подсчитываем "Остальные периоды"
        if other_months:
            total_other_streams = sum(item['streams'] for item in other_months)
            total_other_revenue = sum(item['revenue'] for item in other_months)
            
            monthly_data.append([
                'Остальные периоды',
                format_number(total_other_streams),
                format_currency(total_other_revenue),
                '-',
                '-'
            ])
        
        table = Table(monthly_data, colWidths=[
            self.width * 0.25,
            self.width * 0.2,
            self.width * 0.2,
            self.width * 0.175,
            self.width * 0.175
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_charts(self, data):
        """Add visualizations"""
        self.story.append(PageBreak())
        
        heading = Paragraph("ВИЗУАЛИЗАЦИЯ ДАННЫХ", self.styles['CustomHeading2'])
        self.story.append(heading)
        self.story.append(Spacer(1, 5*mm))
        
        # Revenue by month chart - последние 3 месяца
        try:
            revenue_chart = create_chart_revenue_by_month(data)
            img = Image(revenue_chart, width=150*mm, height=75*mm)
            self.story.append(img)
            self.story.append(Spacer(1, 8*mm))
        except Exception as e:
            print(f"Ошибка создания графика дохода: {e}")
        
        # Platforms pie chart
        try:
            platforms_chart = create_chart_platforms(data)
            img = Image(platforms_chart, width=140*mm, height=100*mm)
            self.story.append(img)
            self.story.append(Spacer(1, 8*mm))
        except Exception as e:
            print(f"Ошибка создания графика платформ: {e}")
        
        self.story.append(PageBreak())
        
        # Countries bar chart
        try:
            countries_chart = create_chart_countries(data)
            img = Image(countries_chart, width=150*mm, height=100*mm)
            self.story.append(img)
        except Exception as e:
            print(f"Ошибка создания графика стран: {e}")
    
    def add_recommendations(self):
        """Add recommendations section"""
        self.story.append(PageBreak())
        
        heading = Paragraph("ВЫВОДЫ И РЕКОМЕНДАЦИИ", self.styles['CustomHeading2'])
        self.story.append(heading)
        
        # Создаем стиль для рекомендаций
        rec_style = ParagraphStyle(
            'RecommendationStyle',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=14
        )
        
        recommendations = [
            "<b>СИЛЬНЫЕ СТОРОНЫ:</b>",
            "- Трек 'Поцелованная солнцем' - абсолютный хит с 65% всех стримов",
            "- Стабильная база в Казахстане (57% стримов)",
            "- Отличная монетизация на Apple Music (EUR 0.0044/стрим)",
            "- Широкий географический охват (145 стран)",
            "",
            "<b>ЗОНЫ ВНИМАНИЯ:</b>",
            "- Резкое падение стримов в декабре (-87%)",
            "- Низкая монетизация на Facebook/Instagram",
            "- Зависимость от одного хита",
            "",
            "<b>РЕКОМЕНДАЦИИ:</b>",
            "- <b>Контент:</b> Новый релиз в стиле 'Поцелованная солнцем'",
            "- <b>Маркетинг:</b> TikTok challenge, фокус на Apple Music playlists",
            "- <b>Платформы:</b> Приоритет Apple Music, Spotify, YouTube",
            "- <b>География:</b> Укрепление позиций в Центральной Азии, развитие китайского рынка",
        ]
        
        for rec in recommendations:
            p = Paragraph(rec, rec_style)
            self.story.append(p)
            self.story.append(Spacer(1, 3*mm))
    
    def add_footer_info(self):
        """Add footer information"""
        self.story.append(Spacer(1, 10*mm))
        
        footer_text = (
            "<para align=center>"
            "───────────────────────────────────────────────────────<br/>"
            "<br/>"
            "Отчёт сгенерирован автоматически системой Music Analyzer Agent<br/>"
            f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>"
            "<br/>"
            "По всем вопросам обращайтесь: ozenxo@gmail.com<br/>"
            "г. Астана, ул. Е-755, д. 1, офис 127"
            "</para>"
        )
        
        footer = Paragraph(footer_text, self.styles['Footer'])
        self.story.append(footer)
    
    def generate(self):
        """Generate the PDF report"""
        print("Генерация PDF отчёта для Mona Songz...")
        
        # Load data
        data = load_json_data()
        
        # Add all sections
        self.add_header(data)
        self.add_kpi_summary(data)
        self.add_medialand_summary()
        self.add_top_tracks(data)
        self.add_platforms_analysis(data)
        self.add_countries_analysis(data)
        self.add_monthly_dynamics(data)
        self.add_charts(data)
        
        # Build PDF
        self.doc.build(self.story)
        
        print(f"✓ PDF отчёт успешно создан: {OUTPUT_PATH}")
        print(f"  Используемые шрифты: {FONT_NAME}, {FONT_NAME_BOLD}")


def main():
    try:
        report = PDFReport()
        report.generate()
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()