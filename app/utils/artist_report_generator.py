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
        """Создает PDF-файл"""
        
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
        
        # Добавляем секции
        story.extend(self._add_header(data, period, styles))
        story.extend(self._add_kpi_summary(data, styles, width))
        story.extend(self._add_top_tracks(data, styles, width))
        story.extend(self._add_platforms(data, styles, width))
        story.extend(self._add_countries(data, styles, width))
        
        # Графики на новой странице
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
    
    def _add_header(self, data: dict, period: str, styles):
        """Добавляет заголовок отчета"""
        elements = []
        
        title = Paragraph("КВАРТАЛЬНЫЙ ОТЧЁТ", styles['CustomTitle'])
        elements.append(title)
        
        subtitle = Paragraph(
            f"<b>Артист:</b> {data['artist_name']}<br/>"
            f"<b>Период:</b> {period}<br/>"
            f"<b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y')}",
            styles['ContactInfo']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 10*mm))
        
        # Контактная информация компании
        contact_info = Paragraph(
            "<b>БИН</b> 190440002324 | <b>ИИК</b> KZ5096503F0008550902 | <b>БИК</b> IRTYKZKA<br/>"
            '<b>АО "ForteBank"</b> г. Астана<br/>'
            "<b>E-mail:</b> ozenxo@gmail.com | <b>Адрес:</b> г. Астана, ул. Е-755, д. 1, офис 127",
            styles['ContactInfo']
        )
        elements.append(contact_info)
        elements.append(Spacer(1, 10*mm))
        
        return elements
    
    def _add_kpi_summary(self, data: dict, styles, width):
        """Добавляет KPI сводку"""
        elements = []
        
        heading = Paragraph("КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ", styles['CustomHeading2'])
        elements.append(heading)
        
        kpi_data = [
            ['Показатель', 'Значение'],
            ['Общие стримы', self._format_number(data['overview']['total_streams'])],
            ['Общий доход (Believe)', self._format_currency(data['overview']['total_revenue'])],
            ['Заработок артиста (74.8%)', self._format_currency(data['overview']['artist_earnings'])],
            ['Уникальных треков', str(data['overview']['unique_tracks'])],
            ['Охват стран', str(data['overview']['unique_countries'])],
            ['Количество платформ', str(data['overview']['unique_platforms'])],
            ['Средняя цена за стрим', self._format_currency(data['financial']['avg_price_per_stream'])],
        ]
        
        table = Table(kpi_data, colWidths=[width * 0.6, width * 0.4])
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
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_top_tracks(self, data: dict, styles, width):
        """Добавляет топ треки"""
        elements = []
        
        heading = Paragraph("ТОП ТРЕКИ", styles['CustomHeading2'])
        elements.append(heading)
        
        tracks_data = [['Трек', 'Стримы', 'Доход (EUR)', '% от дохода']]
        
        total_revenue = data['overview']['total_revenue']
        for track in data['tracks']['tracks']:
            percentage = (track['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            tracks_data.append([
                track['track_name'][:30],
                self._format_number(track['streams']),
                self._format_currency(track['revenue']),
                f"{percentage:.1f}%"
            ])
        
        table = Table(tracks_data, colWidths=[
            width * 0.4,
            width * 0.2,
            width * 0.2,
            width * 0.2
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
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _add_platforms(self, data: dict, styles, width):
        """Добавляет анализ платформ"""
        elements = []
        
        heading = Paragraph("АНАЛИЗ ПЛАТФОРМ (Топ-5)", styles['CustomHeading2'])
        elements.append(heading)
        
        platforms_data = [['Платформа', 'Стримы', 'Доход', '€/стрим']]
        
        for p in data['platforms']['platforms']:
            platforms_data.append([
                p['platform'][:25],
                self._format_number(p['streams']),
                self._format_currency(p['revenue']),
                f"€{p['avg_price_per_stream']:.4f}"
            ])
        
        table = Table(platforms_data, colWidths=[
            width * 0.4,
            width * 0.2,
            width * 0.2,
            width * 0.2
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
        
        elements.append(table)
        elements.append(Spacer(1, 5*mm))
        
        return elements
    
    def _add_countries(self, data: dict, styles, width):
        """Добавляет географию"""
        elements = []
        
        if not data['geography']['top_countries']:
            return elements
        
        heading = Paragraph("ГЕОГРАФИЯ (Топ-10 стран)", styles['CustomHeading2'])
        elements.append(heading)
        
        countries_data = [['Страна', 'Стримы', 'Доход (EUR)', '% стримов']]
        
        for country in data['geography']['top_countries']:
            countries_data.append([
                country['country'][:20],
                self._format_number(country['streams']),
                self._format_currency(country['revenue']),
                f"{country['percentage']:.1f}%"
            ])
        
        table = Table(countries_data, colWidths=[
            width * 0.35,
            width * 0.25,
            width * 0.2,
            width * 0.2
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
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
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

