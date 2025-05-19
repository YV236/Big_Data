# main.py

import requests
import logging
import os
import sys
import glob
from src.data_loader import DataLoader
from src.data_processor import DataProcessor
from src.data_analyzer import DataAnalyzer
from src.data_visualizer import DataVisualizer
from config import (
    get_config, EXTERNAL_API_URL, DATABASE_PATH, FIGURES_OUTPUT_DIR,
    LOGGING_LEVEL, LOGGING_FORMAT,
    DEFAULT_COUNTRIES_TO_ANALYZE, DEFAULT_START_YEAR, DEFAULT_END_YEAR, DEFAULT_FORECAST_YEARS
)

# Налаштування логування
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL),
    format=LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

def setup_environment():
    """
    Створює необхідні директорії для проекту.
    """
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs(FIGURES_OUTPUT_DIR, exist_ok=True)
    os.makedirs("output/reports", exist_ok=True)

def clean_figures_folder():
    figures_dir = "output/figures"
    files = glob.glob(os.path.join(figures_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Could not delete {f}: {e}")

def load_and_process_data():
    """
    Завантажує та обробляє дані про населення.
    
    Returns:
        pandas.DataFrame: Оброблені дані
    """
    # Завантаження даних
    logger.info("Завантаження даних...")
    data_loader = DataLoader(EXTERNAL_API_URL)
    
    try:
        raw_data = data_loader.fetch_data()
        data_path = data_loader.save_data(raw_data)
        logger.info(f"Дані збережено у {data_path}")
    except Exception as e:
        logger.error(f"Помилка при завантаженні даних: {e}")
        sys.exit(1)
    
    # Обробка даних
    logger.info("Обробка даних...")
    data_processor = DataProcessor(DATABASE_PATH)
    
    try:
        processed_data = data_processor.process_data(raw_data)
        data_processor.save_to_database(processed_data)
        logger.info(f"Дані оброблено та збережено у базу даних {DATABASE_PATH}")
        return processed_data
    except Exception as e:
        logger.error(f"Помилка при обробці даних: {e}")
        sys.exit(1)

def analyze_data(processed_data, config):
    """
    Аналізує дані про населення.
    
    Args:
        processed_data (pandas.DataFrame): Оброблені дані
        config (dict): Конфігурація аналізу
    
    Returns:
        tuple: Статистика, прогноз та дані для порівняння
    """
    logger.info("Аналіз даних...")
    data_analyzer = DataAnalyzer()
    
    try:
        # Отримання параметрів з конфігурації
        countries = config['countries']
        start_year = config['start_year']
        end_year = config['end_year']
        forecast_years = config['forecast_years']
        
        # Розрахунок статистики
        stats = data_analyzer.calculate_statistics(processed_data)
        logger.info("Статистичні показники розраховано")
        
        # Прогнозування населення для вибраних країн
        forecasts = {}
        for country in countries:
            forecast = data_analyzer.predict_population(processed_data, country, forecast_years)
            if forecast is not None:
                forecasts[country] = forecast
        
        # Порівняння країн
        comparison_data = data_analyzer.compare_countries(
            processed_data, 
            countries, 
            start_year=start_year, 
            end_year=end_year
        )
        
        return stats, forecasts, comparison_data
    except Exception as e:
        logger.error(f"Помилка при аналізі даних: {e}")
        return None, None, None

def visualize_data(processed_data, forecasts, comparison_data, config):
    """
    Створює візуалізації даних про населення.
    
    Args:
        processed_data (pandas.DataFrame): Оброблені дані
        forecasts (dict): Прогнози населення
        comparison_data (pandas.DataFrame): Дані для порівняння
        config (dict): Конфігурація аналізу
    """
    logger.info("Візуалізація даних...")
    data_visualizer = DataVisualizer(FIGURES_OUTPUT_DIR)
    
    try:
        # Отримання параметрів з конфігурації
        countries = config['countries']
        
        # Графік зростання населення для всіх країн
        data_visualizer.plot_population_growth(processed_data, country=None, start_year=config['start_year'], end_year=config['end_year'])
        data_visualizer.plot_growth_percentage(processed_data, country=None, start_year=config['start_year'], end_year=config['end_year'])
        
        # Графіки зростання населення для кожної країни окремо
        for country in countries:
            country_data = processed_data[processed_data['country'] == country]
            if not country_data.empty:
                data_visualizer.plot_population_growth(country_data, country=country)
                data_visualizer.plot_growth_percentage(country_data, country=country)
        
        # Графік порівняння країн
        if comparison_data is not None:
            data_visualizer.plot_population_comparison(processed_data, countries, start_year=config['start_year'], end_year=config['end_year'])
        
        # Графіки прогнозів
        for country, forecast_df in forecasts.items():
            actual_data = processed_data[processed_data['country'] == country]
            predicted_data = forecast_df[forecast_df['is_predicted'] == True]
            data_visualizer.plot_population_forecast(actual_data, predicted_data, country)
        
        # Теплова карта зростання
        data_visualizer.plot_heatmap(processed_data, countries, start_year=config['start_year'], end_year=config['end_year'])
        
        logger.info(f"Візуалізації збережено у директорії {FIGURES_OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"Помилка при візуалізації даних: {e}")

def generate_report(stats, config):
    """
    Генерує текстовий звіт з результатами аналізу.
    
    Args:
        stats (dict): Статистичні показники
        config (dict): Конфігурація аналізу
    """
    logger.info("Генерація звіту...")
    
    try:
        report_path = "output/reports/population_analysis_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Placeholder for writing the report
            f.write("Population Analysis Report\n")
            f.write("===========================\n")
            f.write("This is a placeholder for the report content.\n")
        logger.info(f"Звіт збережено у файл {report_path}")
    except Exception as e:
        logger.error(f"Помилка при генерації звіту: {e}")

def generate_interactive_pdf(processed_data, config):
    try:
        from borb.pdf import Document
        from borb.pdf import Page
        from borb.pdf import PDF
        from borb.pdf import SingleColumnLayout
        from borb.pdf.canvas.layout.image.image import Image as BorbImage
        from borb.pdf.canvas.layout.text.paragraph import Paragraph
        from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
        from borb.pdf.canvas.layout.table.table import TableCell
        from borb.pdf.canvas.color.color import HexColor
        from decimal import Decimal
        import os
        
        # Створення директорії для звітів
        os.makedirs("output/reports", exist_ok=True)
        
        # Створення документа
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Заголовок
        layout.add(Paragraph(f"Звіт про населення країн", 
                            font="Helvetica-Bold", 
                            font_size=Decimal(20)))
        
        # Інформація про період
        layout.add(Paragraph(f"Період аналізу: {config['start_year']}-{config['end_year']}", 
                            font="Helvetica", 
                            font_size=Decimal(12)))
        layout.add(Paragraph(f"Країни: {', '.join(config['countries'])}", 
                            font="Helvetica", 
                            font_size=Decimal(12)))
        
        # Додавання графіків
        layout.add(Paragraph("Візуалізація даних", 
                            font="Helvetica-Bold", 
                            font_size=Decimal(16)))
        
        # Перевірка наявності графіків
        figures_dir = "output/figures"
        if os.path.exists(figures_dir):
            for filename in os.listdir(figures_dir):
                if filename.endswith(('.png', '.jpg')):
                    img_path = os.path.join(figures_dir, filename)
                    
                    # Назва графіка
                    chart_name = filename.replace('.png', '').replace('_', ' ').title()
                    layout.add(Paragraph(chart_name, 
                                        font="Helvetica-Bold", 
                                        font_size=Decimal(14)))
                    
                    # Додавання зображення
                    layout.add(BorbImage(img_path, width=Decimal(400)))
        
        # Збереження PDF
        pdf_path = "output/reports/population_interactive_report.pdf"
        with open(pdf_path, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, doc)
        
        print(f"Інтерактивний PDF звіт згенеровано: {pdf_path}")
    except ImportError:
        print("Для використання Borb встановіть: pip install borb")

def generate_simple_pdf_report(processed_data, config, stats):
    from fpdf import FPDF
    import os
    
    # Створення директорії для звітів
    os.makedirs("output/reports", exist_ok=True)
    
    # Створення PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Налаштування шрифтів
    pdf.set_font("Arial", "B", 16)
    
    # Заголовок
    pdf.cell(0, 10, "Звіт про населення країн", ln=True, align="C")
    pdf.ln(5)
    
    # Інформація про період
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Період аналізу: {config['start_year']}-{config['end_year']}", ln=True)
    pdf.cell(0, 10, f"Країни: {', '.join(config['countries'])}", ln=True)
    pdf.ln(5)
    
    # Статистика
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Статистичні показники", ln=True)
    pdf.set_font("Arial", "", 12)
    
    if isinstance(stats, dict):
        for key, value in stats.items():
            if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                formatted_key = key.replace('_', ' ').title()
                pdf.cell(0, 10, f"{formatted_key}: {value}", ln=True)
    
    # Додавання графіків
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Візуалізація даних", ln=True)
    
    # Перевірка наявності графіків
    figures_dir = "output/figures"
    if os.path.exists(figures_dir):
        for filename in os.listdir(figures_dir):
            if filename.endswith(('.png', '.jpg')):
                img_path = os.path.join(figures_dir, filename)
                
                # Назва графіка
                chart_name = filename.replace('.png', '').replace('_', ' ').title()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, chart_name, ln=True)
                
                # Додавання зображення
                pdf.image(img_path, x=10, y=None, w=190)
                pdf.ln(5)
    
    # Збереження PDF
    pdf_path = "output/reports/population_simple_report.pdf"
    pdf.output(pdf_path)
    print(f"Простий PDF звіт згенеровано: {pdf_path}")

def generate_pdf_report(processed_data, config, stats):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    import os
    
    # Створення директорії для звітів
    os.makedirs("output/reports", exist_ok=True)
    
    # Створення PDF документа
    doc = SimpleDocTemplate("output/reports/population_report.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    
    # Додавання стилів
    title_style = styles['Title']
    heading_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Заголовок
    elements.append(Paragraph(f"Звіт про населення країн", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Інформація про період
    elements.append(Paragraph(f"Період аналізу: {config['start_year']}-{config['end_year']}", normal_style))
    elements.append(Paragraph(f"Країни: {', '.join(config['countries'])}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Додавання статистики
    elements.append(Paragraph("Статистичні показники", heading_style))
    
    if isinstance(stats, dict):
        data = [["Показник", "Значення"]]
        for key, value in stats.items():
            if isinstance(value, (int, float, str)) and not isinstance(value, bool):
                formatted_key = key.replace('_', ' ').title()
                data.append([formatted_key, str(value)])
        
        table = Table(data, colWidths=[10*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    # Додавання графіків
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("Візуалізація даних", heading_style))
    
    # Перевірка наявності графіків у директорії
    figures_dir = "output/figures"
    if os.path.exists(figures_dir):
        for filename in os.listdir(figures_dir):
            if filename.endswith(('.png', '.jpg')):
                img_path = os.path.join(figures_dir, filename)
                
                # Форматування назви графіка
                chart_name = filename.replace('.png', '').replace('_', ' ').title()
                elements.append(Paragraph(f"{chart_name}", styles['Heading2']))
                
                # Додавання зображення з масштабуванням
                img = Image(img_path)
                img.drawHeight = 10*cm
                img.drawWidth = 15*cm
                elements.append(img)
                elements.append(Spacer(1, 0.5*cm))
    
    # Побудова документа
    doc.build(elements)
    print(f"PDF звіт згенеровано: output/reports/population_report.pdf")


def export_data_for_bi(processed_data, comparison_data, stats):
    """
    Експортує дані у різні формати для інтеграції з BI-інструментами.
    
    Args:
        processed_data: DataFrame з обробленими даними
        comparison_data: DataFrame з даними для порівняння
        stats: DataFrame зі статистикою
    """
    # Експорт у CSV
    if processed_data is not None:
        DataProcessor.export_to_csv(processed_data, "przetworzone_dane.csv")
    if comparison_data is not None:
        DataProcessor.export_to_csv(comparison_data, "porownanie_krajow.csv")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_csv(stats.head(5), "top5_krajow.csv")

    # Експорт в Excel (з правильним розширенням!)
    if processed_data is not None:
        DataProcessor.export_to_excel(processed_data, "przetworzone_dane.xlsx")
    if comparison_data is not None:
        DataProcessor.export_to_excel(comparison_data, "porownanie_krajow.xlsx")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_excel(stats.head(5), "top5_krajow.xlsx")
        
    # Експорт в JSON
    if processed_data is not None:
        DataProcessor.export_to_json(processed_data, "przetworzone_dane.json")
    if comparison_data is not None:
        DataProcessor.export_to_json(comparison_data, "porownanie_krajow.json")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_json(stats.head(5), "top5_krajow.json")
        
    print("Дані успішно експортовано для інтеграції з BI-інструментами")



def main():
    """
    Головна функція для запуску проекту Population Analysis.
    """
    logger.info("Запуск проекту Population Analysis")
    
    # Отримання списку країн з API
    logger.info("Отримання списку доступних країн...")
    try:
        response = requests.get(EXTERNAL_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # ...po pobraniu danych z API...
        raw_countries = [item['country'] for item in data['data']]
        # Lista słów kluczowych, które mogą oznaczać region/agregat
        region_keywords = [
            "countries", "region", "income", "IDA", "IBRD", "aggregate", "total", "area", "Euro area"
        ]
        # Filtrowanie tylko krajów (bez regionów/agregatów)
        available_countries = [
            country for country in raw_countries
            if not any(keyword.lower() in country.lower() for keyword in region_keywords)
        ]
        
        # Виведення списку країн
        print("\nДоступні країни:")
        for i, country in enumerate(available_countries, 1):
            print(f"{i}. {country}")
            # Додаємо паузу після кожних 20 країн для зручності читання
            if i % 20 == 0 and i < len(available_countries):
                input("Натисніть Enter для продовження...")
        
        # Вибір країн користувачем
        selected_countries = []
        while not selected_countries:
            print("\nВиберіть країни для аналізу (введіть номери через кому):")
            country_indices = input("> ").strip().split(',')
            for idx in country_indices:
                try:
                    index = int(idx.strip()) - 1
                    if 0 <= index < len(available_countries):
                        selected_countries.append(available_countries[index])
                except ValueError:
                    pass
            if not selected_countries:
                print("Не вибрано жодної країни. Спробуйте ще раз.")

        # Вибір початкового року
        while True:
            print("\nВведіть початковий рік (наприклад, 1960):")
            start_year_input = input("> ").strip()
            if start_year_input.isdigit():
                start_year = int(start_year_input)
                if 1960 <= start_year <= 2018:
                    break
                else:
                    print("Рік повинен бути в межах 1960-2018. Спробуйте ще раз.")
            else:
                print("Некоректне значення. Спробуйте ще раз.")

        # Вибір кінцевого року
        while True:
            print("\nВведіть кінцевий рік (наприклад, 2018):")
            end_year_input = input("> ").strip()
            if end_year_input.isdigit():
                end_year = int(end_year_input)
                if 1960 <= end_year <= 2018 and end_year >= start_year:
                    break
                elif end_year < start_year:
                    print("Кінцевий рік не може бути менший за початковий. Спробуйте ще раз.")
                else:
                    print("Рік повинен бути в межах 1960-2018. Спробуйте ще раз.")
            else:
                print("Некоректне значення. Спробуйте ще раз.")

        # Створення конфігурації на основі вибору користувача
        config = {
            'countries': selected_countries,
            'start_year': start_year,
            'end_year': end_year,
            'forecast_years': DEFAULT_FORECAST_YEARS
        }
        
        # Створення необхідних директорій
        setup_environment()
        
        # Очистка папки з графіками
        clean_figures_folder()
        
        # Завантаження та обробка даних
        processed_data = load_and_process_data()
        
        # Аналіз даних
        stats, forecasts, comparison_data = analyze_data(processed_data, config)

        if processed_data is not None:
            export_data_for_bi(processed_data, comparison_data, stats)

        # Візуалізація даних
        if processed_data is not None:
            visualize_data(processed_data, forecasts, comparison_data, config)
        
        # Генерація звіту
        if stats is not None:
            generate_report(stats, config)

        # Після аналізу даних
        if stats is not None:
            # Генерація PDF-звітів
            generate_pdf_report(processed_data, config, stats)
            generate_simple_pdf_report(processed_data, config, stats)
            generate_interactive_pdf(processed_data, config)

        
        logger.info("Проект успішно завершено")
        print("\nАналіз завершено. Результати збережено у директоріях:")
        print(f"- Графіки: {FIGURES_OUTPUT_DIR}")
        print("- Звіти: output/reports")
        
    except Exception as e:
        logger.error(f"Помилка при виконанні програми: {e}")
        print(f"Сталася помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()