"""
Artist Report Generator - Creates professional PDF reports
Based on generate_mona_songz_pdf.py structure
"""

import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import logging

logger = logging.getLogger(__name__)

# Регистрация шрифтов с поддержкой кириллицы
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
    logger.info("✓ Загружены шрифты Arial Unicode")
except:
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/Library/Fonts/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/Library/Fonts/DejaVuSans-Bold.ttf'))
        FONT_NAME = 'DejaVuSans'
        FONT_NAME_BOLD = 'DejaVuSans-Bold'
        logger.info("✓ Загружены шрифты DejaVu Sans")
    except:
        FONT_NAME = 'Helvetica'
        FONT_NAME_BOLD = 'Helvetica-Bold'
        logger.warning("⚠ Используются шрифты без кириллицы")

# Matplotlib для кириллицы
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Arial']


class ArtistReportGenerator:
    """Генератор профессиональных PDF-отчетов для артистов"""
    
    def __init__(self, analytics_service):
        self.analytics = analytics_service
        self.base_dir = Path(__file__).parent.parent.parent
        self.reports_dir = self.base_dir / "reports" / "artist_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, artist_name: str, period: str = "Q4 2025", include_medialand: bool = False):
        """
        Генерирует PDF-отчет для артиста
        
        Args:
            artist_name: Имя артиста
            period: Период отчета (например, "Q4 2025")
            include_medialand: Включить данные Medialand
            
        Returns:
            dict с результатом генерации
        """
        try:
            logger.info(f"📊 Начало генерации отчета для {artist_name}")
            
            # 1. Собираем данные артиста
            data = self._collect_artist_data(artist_name, period)
            
            if not data:
                return {
                    "success": False,
                    "error": f"Артист '{artist_name}' не найден в базе данных"
                }
            
            # 2. Создаем PDF
            pdf_path = self._create_pdf(data, period, include_medialand)
            
            # 3. Формируем краткую сводку
            summary = self._create_summary(data)
            
            return {
                "success": True,
                "artist_name": data['artist_name'],
                "pdf_path": str(pdf_path),
                "pdf_filename": pdf_path.name,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _collect_artist_data(self, artist_name: str, period: str):
        """Собирает все данные артиста из analytics_service"""
        
        # Получаем данные через AnalyticsService
        df = self.analytics._df.copy()
        
        # Поиск артиста (нечувствительно к регистру, частичное совпадение)
        artist_mask = df['Исполнитель'].str.lower().str.contains(artist_name.lower(), na=False)
        artist_df = df[artist_mask].copy()
        
        if len(artist_df) == 0:
            return None
        
        # Определяем точное имя артиста (самый частый вариант)
        exact_name = artist_df['Исполнитель'].mode()[0]
        
        # Конвертируем числовые колонки если они строки
        if artist_df['Сумма вознаграждения'].dtype == 'object':
            artist_df['Сумма вознаграждения'] = pd.to_numeric(artist_df['Сумма вознаграждения'].astype(str).str.replace(',', '.'), errors='coerce')
        if artist_df['Количество'].dtype == 'object':
            artist_df['Количество'] = pd.to_numeric(artist_df['Количество'].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Общая статистика
        total_revenue = float(artist_df['Сумма вознаграждения'].sum())
        total_streams = float(artist_df['Количество'].sum())
        unique_tracks = artist_df['Название трека'].nunique()
        unique_platforms = artist_df['Платформа'].nunique()
        unique_countries = artist_df['страна / регион'].nunique() if 'страна / регион' in artist_df.columns else 0
        
        # Топ-5 платформ
        platforms = artist_df.groupby('Платформа').agg({
            'Количество': 'sum',
            'Сумма вознаграждения': 'sum'
        }).reset_index()
        platforms.columns = ['platform', 'streams', 'revenue']
        platforms['percentage'] = (platforms['revenue'] / total_revenue * 100).round(2)
        platforms['avg_price_per_stream'] = (platforms['revenue'] / platforms['streams']).round(6)
        top_platforms = platforms.sort_values('revenue', ascending=False).head(5).to_dict('records')
        
        # Топ-10 стран
        if 'страна / регион' in artist_df.columns:
            countries = artist_df.groupby('страна / регион').agg({
                'Количество': 'sum',
                'Сумма вознаграждения': 'sum'
            }).reset_index()
            countries.columns = ['country', 'streams', 'revenue']
            countries['percentage'] = (countries['streams'] / total_streams * 100).round(2)
            top_countries = countries.sort_values('revenue', ascending=False).head(10).to_dict('records')
        else:
            top_countries = []
        
        # Топ-10 треков
        tracks = artist_df.groupby('Название трека').agg({
            'Количество': 'sum',
            'Сумма вознаграждения': 'sum'
        }).reset_index()
        tracks.columns = ['track_name', 'streams', 'revenue']
        top_tracks = tracks.sort_values('streams', ascending=False).head(10).to_dict('records')
        
        # Динамика по месяцам
        if 'Месяц отчета' in artist_df.columns:
            monthly = artist_df.groupby('Месяц отчета').agg({
                'Количество': 'sum',
                'Сумма вознаграждения': 'sum'
            }).reset_index().sort_values('Месяц отчета')
            monthly.columns = ['month', 'streams', 'revenue']
            monthly['month'] = monthly['month'].dt.strftime('%Y/%m/%d')
            monthly_data = monthly.to_dict('records')
        else:
            monthly_data = []
        
        return {
            'artist_name': exact_name,
            'overview': {
                'total_streams': int(total_streams),
                'total_revenue': round(total_revenue, 2),
                'artist_earnings': round(total_revenue * 0.748, 2),  # 74.8% для артиста
                'unique_tracks': unique_tracks,
                'unique_platforms': unique_platforms,
                'unique_countries': unique_countries
            },
            'financial': {
                'avg_price_per_stream': round(total_revenue / total_streams, 6) if total_streams > 0 else 0
            },
            'platforms': {
                'platforms': top_platforms
            },
            'geography': {
                'top_countries': top_countries
            },
            'tracks': {
                'tracks': top_tracks
            },
            'time_series': {
                'by_sales_month': monthly_data
            }
        }
    
    def _create_pdf(self, data: dict, period: str, include_medialand: bool):
        """Создает PDF-файл в стиле özen отчетов"""
        
        # Формируем имя файла
        safe_name = "".join(c for c in data['artist_name'] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_Report_{timestamp}.pdf"
        pdf_path = self.reports_dir / filename
        
        # Создаем PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        styles = self._get_styles()
        width = A4[0] - 40*mm
        
        # СТРАНИЦА 1: Заголовок и основная информация
        story.extend(self._add_ozen_header(data, period, styles))
        story.extend(self._add_greeting(data, styles))
        story.extend(self._add_summary_info(data, period, styles))
        story.extend(self._add_payment_summary(data, styles, width))
        story.extend(self._add_footer(styles))
        
        # СТРАНИЦА 2: Аналитика топ трека и платформ
        story.append(PageBreak())
        story.extend(self._add_analytics_header(data, styles))
        story.extend(self._add_top_track_analysis(data, styles, width))
        story.extend(self._add_platforms_revenue_analysis(data, styles, width))
        story.extend(self._add_top_tracks_table(data, styles, width))
        
        # СТРАНИЦА 3: Визуализация (опционально)
        if len(data['platforms']['platforms']) > 0 and len(data['geography']['top_countries']) > 0:
            story.append(PageBreak())
            story.extend(self._add_charts(data, styles, width))
        
        # Строим PDF
        doc.build(story)
        
        logger.info(f"✅ PDF создан: {pdf_path}")
        return pdf_path
    
    def _get_styles(self):
        """Создает стили для PDF"""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontName=FONT_NAME_BOLD,
            fontSize=24,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontName=FONT_NAME_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=10,
            spaceBefore=15
        ))
        
        styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#424242')
        ))
        
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
        
        return styles
    
    def _add_ozen_header(self, data: dict, period: str, styles):
        """Добавляет заголовок в стиле özen"""
        elements = []
        
        # Логотип/название компании
        title = Paragraph("<font size=18><b>özen</b></font>", styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 5*mm))
        
        # Реквизиты компании
        company_info = Paragraph(
            "<font size=8>"
            "<b>БИН</b> 190440002324 | <b>ИИК</b> KZ5096503F0008550902 | <b>БИК</b> IRTYKZKA | АО \"ForteBank\" г.Астана<br/>"
            "e-mail: ozenxo@gmail.com | г. Астана, ул. E-755, д. 1, офис 127"
            "</font>",
            styles['ContactInfo']
        )
        elements.append(company_info)
        elements.append(Spacer(1, 10*mm))
        
        # Дата
        date_text = Paragraph(
            f"<font size=10>{datetime.now().strftime('%d %B %Y года')}</font>",
            styles['Normal']
        )
        elements.append(date_text)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_greeting(self, data: dict, styles):
        """Добавляет приветствие"""
        elements = []
        
        greeting = Paragraph(
            f"<font size=11>Здравствуйте!</font>",
            styles['Normal']
        )
        elements.append(greeting)
        elements.append(Spacer(1, 6*mm))
        
        intro = Paragraph(
            f"<font size=10>Вот общая сумма лицензионных отчислений за нижеперечисленные релизы "
            f"с учетом комиссии за дистрибуцию, составляющую 20%</font>",
            styles['Normal']
        )
        elements.append(intro)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_summary_info(self, data: dict, period: str, styles):
        """Добавляет краткую информацию о каталоге"""
        elements = []
        
        # Получаем список треков
        tracks_list = ", ".join([t['track_name'] for t in data['tracks']['tracks'][:5]])
        if len(data['tracks']['tracks']) > 5:
            tracks_list += f" и ещё {len(data['tracks']['tracks']) - 5} треков"
        
        info = Paragraph(
            f"<font size=10>"
            f"<b>Артист:</b> {data['artist_name']}<br/><br/>"
            f"<b>Релизы:</b> {tracks_list}<br/><br/>"
            f"<b>Период:</b> {period}<br/>"
            "</font>",
            styles['Normal']
        )
        elements.append(info)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_payment_summary(self, data: dict, styles, width):
        """Добавляет сводку по выплатам"""
        elements = []
        
        overview = data['overview']
        
        # Конвертируем EUR в KZT (примерный курс 520 KZT за 1 EUR)
        eur_to_kzt = 520
        distribution_payment = overview['total_revenue'] * eur_to_kzt
        copyright_payment = distribution_payment * 0.08  # Примерно 8% от дистрибуции
        total_payment = distribution_payment + copyright_payment
        
        # Таблица выплат
        payment_data = [
            [Paragraph('<b>Выплата дистрибуция:</b>', styles['Normal']), 
             Paragraph(f'<b>{distribution_payment:,.0f} тенге</b>'.replace(',', ' '), styles['Normal'])],
            [Paragraph('<b>Выплата за авторские сборы:</b>', styles['Normal']), 
             Paragraph(f'<b>{copyright_payment:,.0f} тенге</b>'.replace(',', ' '), styles['Normal'])],
            ['', ''],
            [Paragraph('<b><font size=12>Общая сумма к выплате:</font></b>', styles['Normal']), 
             Paragraph(f'<b><font size=12>{total_payment:,.0f} тенге</font></b>'.replace(',', ' '), styles['Normal'])],
        ]
        
        table = Table(payment_data, colWidths=[width * 0.6, width * 0.4])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 3), (-1, 3), 2, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 15*mm))
        
        return elements
    
    def _add_footer(self, styles):
        """Добавляет подвал с подписью"""
        elements = []
        
        signature = Paragraph(
            "<font size=10>"
            "С наилучшими пожеланиями,<br/>"
            "сотрудник отдела лицензионных платежей<br/><br/>"
            "<b>özen</b>"
            "</font>",
            styles['Normal']
        )
        elements.append(signature)
        elements.append(Spacer(1, 5*mm))
        
        divider = Paragraph("_" * 80, styles['Footer'])
        elements.append(divider)
        
        return elements
    
    def _add_analytics_header(self, data: dict, styles):
        """Добавляет заголовок аналитической страницы"""
        elements = []
        
        title = Paragraph(
            f"<font size=16><b>Детальная аналитика: {data['artist_name']}</b></font>",
            styles['CustomHeading2']
        )
        elements.append(title)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_top_track_analysis(self, data: dict, styles, width):
        """Добавляет анализ самого популярного и прибыльного трека"""
        elements = []
        
        heading = Paragraph("🎵 САМЫЙ ПОПУЛЯРНЫЙ И ПРИБЫЛЬНЫЙ ТРЕК", styles['CustomHeading2'])
        elements.append(heading)
        elements.append(Spacer(1, 5*mm))
        
        # Находим топ трек по стримам и по доходу
        tracks = data['tracks']['tracks']
        if not tracks:
            return elements
        
        top_by_streams = max(tracks, key=lambda x: x['streams'])
        top_by_revenue = max(tracks, key=lambda x: x['revenue'])
        
        # Данные для таблицы
        track_data = [
            ['Критерий', 'Название трека', 'Стримы', 'Доход (EUR)', '% от дохода'],
        ]
        
        total_revenue = data['overview']['total_revenue']
        
        # Самый популярный (по стримам)
        streams_pct = (top_by_streams['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        track_data.append([
            '🔥 По стримам',
            top_by_streams['track_name'][:30],
            self._format_number(top_by_streams['streams']),
            self._format_currency(top_by_streams['revenue']),
            f"{streams_pct:.1f}%"
        ])
        
        # Самый прибыльный (по доходу) - только если это другой трек
        if top_by_revenue['track_name'] != top_by_streams['track_name']:
            revenue_pct = (top_by_revenue['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            track_data.append([
                '💰 По доходу',
                top_by_revenue['track_name'][:30],
                self._format_number(top_by_revenue['streams']),
                self._format_currency(top_by_revenue['revenue']),
                f"{revenue_pct:.1f}%"
            ])
        
        table = Table(track_data, colWidths=[
            width * 0.18,
            width * 0.35,
            width * 0.17,
            width * 0.15,
            width * 0.15
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.Color(0.95, 0.98, 0.95), colors.white]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_platforms_revenue_analysis(self, data: dict, styles, width):
        """Добавляет анализ платформ по доходу"""
        elements = []
        
        heading = Paragraph("📱 ПЛАТФОРМЫ ПО ДОХОДУ", styles['CustomHeading2'])
        elements.append(heading)
        elements.append(Spacer(1, 5*mm))
        
        platforms = data['platforms']['platforms']
        if not platforms:
            return elements
        
        # Данные для таблицы
        platform_data = [
            ['Место', 'Платформа', 'Стримы', 'Доход (EUR)', '% от дохода', '€/стрим'],
        ]
        
        total_revenue = data['overview']['total_revenue']
        
        for idx, p in enumerate(platforms, 1):
            percentage = (p['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            
            # Эмодзи для топ-3
            emoji = ''
            if idx == 1:
                emoji = '🥇 '
            elif idx == 2:
                emoji = '🥈 '
            elif idx == 3:
                emoji = '🥉 '
            
            platform_data.append([
                f'{emoji}{idx}',
                p['platform'][:25],
                self._format_number(p['streams']),
                self._format_currency(p['revenue']),
                f"{percentage:.1f}%",
                f"€{p['avg_price_per_stream']:.4f}"
            ])
        
        table = Table(platform_data, colWidths=[
            width * 0.12,
            width * 0.30,
            width * 0.18,
            width * 0.16,
            width * 0.12,
            width * 0.12
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.Color(0.93, 0.96, 0.99), colors.white]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
        # Добавляем краткий вывод
        top_platform = platforms[0]
        conclusion = Paragraph(
            f"<font size=10>"
            f"<b>💡 Вывод:</b> Основной доход ({top_platform['percentage']:.1f}%) приходит с платформы "
            f"<b>{top_platform['platform']}</b> ({self._format_currency(top_platform['revenue'])})."
            "</font>",
            styles['Normal']
        )
        elements.append(conclusion)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_top_tracks_table(self, data: dict, styles, width):
        """Добавляет таблицу всех топ треков"""
        elements = []
        
        heading = Paragraph("🎼 ВСЕ ТРЕКИ В КАТАЛОГЕ", styles['CustomHeading2'])
        elements.append(heading)
        elements.append(Spacer(1, 5*mm))
        
        tracks = data['tracks']['tracks']
        if not tracks:
            return elements
        
        # Данные для таблицы
        tracks_data = [['№', 'Название трека', 'Стримы', 'Доход (EUR)', '% дохода']]
        
        total_revenue = data['overview']['total_revenue']
        
        for idx, track in enumerate(tracks[:15], 1):  # Показываем максимум 15 треков
            percentage = (track['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            tracks_data.append([
                str(idx),
                track['track_name'][:35],
                self._format_number(track['streams']),
                self._format_currency(track['revenue']),
                f"{percentage:.1f}%"
            ])
        
        table = Table(tracks_data, colWidths=[
            width * 0.08,
            width * 0.44,
            width * 0.18,
            width * 0.16,
            width * 0.14
        ])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9C27B0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.95, 0.98)]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 5*mm))
        
        return elements
    
    
    def _add_charts(self, data: dict, styles, width):
        """Добавляет графики"""
        elements = []
        
        heading = Paragraph("ВИЗУАЛИЗАЦИЯ ДАННЫХ", styles['CustomHeading2'])
        elements.append(heading)
        elements.append(Spacer(1, 5*mm))
        
        # График платформ
        try:
            platforms_chart = self._create_platforms_chart(data)
            if platforms_chart:
                img = Image(platforms_chart, width=140*mm, height=100*mm)
                elements.append(img)
                elements.append(Spacer(1, 8*mm))
        except Exception as e:
            logger.warning(f"Не удалось создать график платформ: {e}")
        
        # График стран
        if data['geography']['top_countries']:
            try:
                countries_chart = self._create_countries_chart(data)
                if countries_chart:
                    img = Image(countries_chart, width=150*mm, height=100*mm)
                    elements.append(img)
            except Exception as e:
                logger.warning(f"Не удалось создать график стран: {e}")
        
        return elements
    
    def _create_platforms_chart(self, data):
        """Создает пай-чарт платформ"""
        platforms = data['platforms']['platforms'][:5]
        
        if not platforms:
            return None
        
        labels = [p['platform'][:15] for p in platforms]
        revenues = [p['revenue'] for p in platforms]
        
        plt.figure(figsize=(7, 5))
        colors_list = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        plt.pie(revenues, labels=labels, autopct='%1.1f%%', 
                colors=colors_list, startangle=90)
        plt.title('Топ-5 платформ по доходу', fontsize=12, fontweight='bold')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def _create_countries_chart(self, data):
        """Создает бар-чарт стран"""
        countries = data['geography']['top_countries'][:8]
        
        if not countries:
            return None
        
        country_names = [c['country'][:15] for c in countries]
        revenues = [c['revenue'] for c in countries]
        
        plt.figure(figsize=(8, 5))
        plt.barh(country_names, revenues, color='#5C6BC0', alpha=0.8)
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
    
    def _create_summary(self, data: dict):
        """Создает краткую сводку для ответа"""
        overview = data['overview']
        top_track = data['tracks']['tracks'][0] if data['tracks']['tracks'] else None
        top_platform = data['platforms']['platforms'][0] if data['platforms']['platforms'] else None
        
        summary = f"""📊 **Основные показатели:**
- Всего стримов: {self._format_number(overview['total_streams'])}
- Общий доход: {self._format_currency(overview['total_revenue'])}
- Заработок артиста: {self._format_currency(overview['artist_earnings'])}
- Уникальных треков: {overview['unique_tracks']}
"""
        
        if top_track:
            summary += f"\n🎵 **Топ трек:** {top_track['track_name']} ({self._format_number(top_track['streams'])} стримов)"
        
        if top_platform:
            summary += f"\n📱 **Топ платформа:** {top_platform['platform']} ({top_platform['percentage']}% дохода)"
        
        return summary
    
    def _format_number(self, num):
        """Форматирует число с пробелами"""
        if isinstance(num, (int, float)):
            return f"{int(num):,}".replace(',', ' ')
        return str(num)
    
    def _format_currency(self, amount, currency='EUR'):
        """Форматирует валюту"""
        if isinstance(amount, (int, float)):
            if currency == 'EUR':
                return f"€{amount:,.2f}".replace(',', ' ')
        return str(amount)

