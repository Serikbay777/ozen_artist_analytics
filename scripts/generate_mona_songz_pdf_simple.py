#!/usr/bin/env python3
"""
Simple PDF Report Generator for Mona Songz - Quarterly Payments Report
Minimalistic table-based design with Cyrillic support
"""

import json
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ВАЖНО: Регистрация шрифтов с поддержкой кириллицы
try:
    # Для macOS
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
except:
    try:
        # Альтернатива для macOS
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/Library/Fonts/Arial Unicode.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/Library/Fonts/Arial Unicode.ttf'))
        FONT_NAME = 'DejaVuSans'
        FONT_NAME_BOLD = 'DejaVuSans-Bold'
    except:
        print("ВНИМАНИЕ: Не удалось загрузить шрифты с кириллицей. Установите DejaVu Sans.")
        FONT_NAME = 'Helvetica'
        FONT_NAME_BOLD = 'Helvetica-Bold'

# Paths (остается без изменений)
JSON_PATH = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/Mona_Songz_quarter_report.json"
MEDIALAND_SUMMARY = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_summary_medialand.csv"
MEDIALAND_MONTHLY = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_monthly_medialand.csv"
MEDIALAND_PLATFORMS = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_platforms_medialand.csv"
MEDIALAND_COUNTRIES = "/Users/nuraliserikbay/Desktop/codes/music_analyzer_agent/reports/medialand/Mona_Songz_countries_medialand.csv"
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


def format_number(num):
    """Format number with thousand separators"""
    if isinstance(num, (int, float)):
        return f"{num:,.0f}".replace(',', ' ')
    return str(num)


def format_currency_eur(amount):
    """Format EUR currency"""
    if isinstance(amount, (int, float)):
        return f"€{amount:,.2f}".replace(',', ' ')
    return str(amount)


def format_currency_kzt(amount):
    """Format KZT currency"""
    if isinstance(amount, (int, float)):
        return f"{amount:,.0f} ₸".replace(',', ' ')
    return str(amount)


class SimplePDFReport:
    def __init__(self):
        self.doc = SimpleDocTemplate(
            OUTPUT_PATH,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.width = A4[0] - 30*mm
        
        # Стили с кириллическими шрифтами
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME_BOLD,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportHeading',
            parent=self.styles['Heading2'],
            fontName=FONT_NAME_BOLD,
            fontSize=12,
            spaceAfter=6,
            spaceBefore=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=8,
            alignment=TA_CENTER
        ))
    
    def add_simple_table(self, data, col_widths=None, header_bg=colors.HexColor('#4a5a8a')):
        """Add a simple table"""
        if col_widths is None:
            col_widths = [self.width / len(data[0])] * len(data[0])
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),  # Изменено
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),  # Изменено
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 5*mm))
    
    def add_header(self, data):
        """Add report header"""
        # Title
        title = Paragraph("КВАРТАЛЬНЫЙ ОТЧЕТ ПО ВЫПЛАТАМ", self.styles['ReportTitle'])
        self.story.append(title)
        
        # Basic info table
        info_data = [
            ['Артист:', data['artist_name']],
            ['Период:', f"Q4 2025 ({data['period']['start']} - {data['period']['end']})"],
            ['Дата отчета:', datetime.now().strftime('%d.%m.%Y')],
        ]
        
        info_table = Table(info_data, colWidths=[self.width * 0.3, self.width * 0.7])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), FONT_NAME_BOLD),
            ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        self.story.append(info_table)
        self.story.append(Spacer(1, 3*mm))
        
        # Contact info table
        contact_data = [
            ['БИН', '190440002324'],
            ['ИИК', 'KZ50965Q3F0008550902'],
            ['БИК', 'IRTYKZKA'],
            ['Банк', 'АО "ForteBank" г.Астана'],
            ['E-mail', 'ozenxo@gmail.com'],
            ['Адрес', 'г. Астана, ул. Е-755, д. 1, офис 127'],
        ]
        
        contact_table = Table(contact_data, colWidths=[self.width * 0.2, self.width * 0.8])
        contact_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), FONT_NAME_BOLD),
            ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        self.story.append(contact_table)
        self.story.append(Spacer(1, 8*mm))
    
    def add_kpi_summary(self, data):
        """Add KPI summary"""
        heading = Paragraph("1. КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ", self.styles['ReportHeading'])
        self.story.append(heading)
        
        kpi_data = [
            ['Показатель', 'Значение'],
            ['Общие стримы', format_number(data['overview']['total_streams'])],
            ['Общий доход (Believe)', format_currency_eur(data['overview']['total_revenue'])],
            ['Заработок артиста (74.8%)', format_currency_eur(data['overview']['artist_earnings'])],
            ['Уникальных треков', str(data['overview']['unique_tracks'])],
            ['Уникальных релизов', str(data['overview']['unique_releases'])],
            ['Охват стран', str(data['overview']['unique_countries'])],
            ['Количество платформ', str(data['overview']['unique_platforms'])],
            ['Средняя цена за стрим', format_currency_eur(data['financial']['avg_price_per_stream'])],
        ]
        
        self.add_simple_table(kpi_data, [self.width * 0.6, self.width * 0.4])
    
    # Остальные методы аналогично...
    # (continue with other methods, replacing all font references)

    def generate(self):
        """Generate the PDF report"""
        print("Генерация PDF отчета для Mona Songz...")
        
        # Load data
        data = load_json_data()
        
        # Add all sections
        self.add_header(data)
        self.add_kpi_summary(data)
        # ... остальные секции
        
        # Build PDF
        self.doc.build(self.story)
        
        print(f"PDF отчет успешно создан: {OUTPUT_PATH}")


def main():
    try:
        report = SimplePDFReport()
        report.generate()
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()