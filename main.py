# main.py

import requests
import logging
import os
import sys
from src.data_loader import DataLoader
from src.data_processor import DataProcessor
from src.data_analyzer import DataAnalyzer
from src.data_visualizer import DataVisualizer
from config import get_config, EXTERNAL_API_URL, DATABASE_PATH, FIGURES_OUTPUT_DIR, LOGGING_LEVEL, LOGGING_FORMAT

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
        data_visualizer.plot_population_growth(processed_data)
        
        # Графіки зростання населення для кожної країни окремо
        for country in countries:
            country_data = processed_data[processed_data['country'] == country]
            if not country_data.empty:
                data_visualizer.plot_population_growth(country_data, country=country)
                data_visualizer.plot_growth_percentage(country_data, country=country)
        
        # Графік порівняння країн
        if comparison_data is not None:
            data_visualizer.plot_population_comparison(comparison_data, countries)
        
        # Графіки прогнозів
        for country, forecast_df in forecasts.items():
            actual_data = processed_data[processed_data['country'] == country]
            predicted_data = forecast_df[forecast_df['is_predicted'] == True]
            data_visualizer.plot_population_forecast(actual_data, predicted_data, country)
        
        # Теплова карта зростання
        data_visualizer.plot_heatmap(processed_data, countries)
        
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
            f.write("=== ЗВІТ ПРО АНАЛІЗ НАСЕЛЕННЯ ===\n\n")
            
            # Параметри аналізу
            f.write("Параметри аналізу:\n")
            f.write(f"- Країни: {', '.join(config['countries'])}\n")
            f.write(f"- Період: {config['start_year']}-{config['end_year']}\n")
            f.write(f"- Прогноз на {config['forecast_years']} років\n\n")
            
            # Статистичні показники
            if stats:
                f.write("Статистичні показники:\n")
                f.write(f"- Загальна кількість країн: {stats['total_countries']}\n")
                f.write(f"- Діапазон років: {stats['year_range'][0]}-{stats['year_range'][1]}\n")
                f.write(f"- Загальне населення на початку періоду: {stats['total_population_start']:,}\n")
                f.write(f"- Загальне населення в кінці періоду: {stats['total_population_end']:,}\n")
                f.write(f"- Загальний приріст населення: {stats['total_growth_percentage']:.2f}%\n")
                f.write(f"- Середній щорічний приріст: {stats['avg_annual_growth_percentage']:.2f}%\n\n")
                
                f.write("Країни з найбільшим та найменшим населенням:\n")
                f.write(f"- Найбільше населення: {stats['largest_population_country']} ({stats['largest_population_value']:,})\n")
                f.write(f"- Найменше населення: {stats['smallest_population_country']} ({stats['smallest_population_value']:,})\n\n")
                
                f.write("Країни з найбільшим та найменшим приростом:\n")
                f.write(f"- Найбільший приріст: {stats['highest_growth_country']} ({stats['highest_growth_percentage']:.2f}%)\n")
                f.write(f"- Найменший приріст: {stats['lowest_growth_country']} ({stats['lowest_growth_percentage']:.2f}%)\n")
            
            f.write("\n=== КІНЕЦЬ ЗВІТУ ===\n")
        
        logger.info(f"Звіт збережено у файл {report_path}")
    except Exception as e:
        logger.error(f"Помилка при генерації звіту: {e}")

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
        available_countries = [item['country'] for item in data['data']]
        
        # Виведення списку країн
        print("\nДоступні країни:")
        for i, country in enumerate(available_countries, 1):
            print(f"{i}. {country}")
            # Додаємо паузу після кожних 20 країн для зручності читання
            if i % 20 == 0 and i < len(available_countries):
                input("Натисніть Enter для продовження...")
        
        # Вибір країн користувачем
        print("\nВиберіть країни для аналізу (введіть номери через кому):")
        country_indices = input("> ").strip().split(',')
        selected_countries = []
        for idx in country_indices:
            try:
                index = int(idx.strip()) - 1
                if 0 <= index < len(available_countries):
                    selected_countries.append(available_countries[index])
            except ValueError:
                pass
        
        if not selected_countries:
            print("Не вибрано жодної країни. Використовуємо значення за замовчуванням.")
            selected_countries = DEFAULT_COUNTRIES_TO_ANALYZE
        
        # Вибір діапазону років
        print("\nВведіть початковий рік (наприклад, 1960):")
        start_year = input("> ").strip()
        try:
            start_year = int(start_year)
        except ValueError:
            print(f"Некоректне значення. Використовуємо значення за замовчуванням: {DEFAULT_START_YEAR}")
            start_year = DEFAULT_START_YEAR
        
        print("\nВведіть кінцевий рік (наприклад, 2018):")
        end_year = input("> ").strip()
        try:
            end_year = int(end_year)
        except ValueError:
            print(f"Некоректне значення. Використовуємо значення за замовчуванням: {DEFAULT_END_YEAR}")
            end_year = DEFAULT_END_YEAR
        
        # Створення конфігурації на основі вибору користувача
        config = {
            'countries': selected_countries,
            'start_year': start_year,
            'end_year': end_year,
            'forecast_years': DEFAULT_FORECAST_YEARS
        }
        
        # Створення необхідних директорій
        setup_environment()
        
        # Завантаження та обробка даних
        processed_data = load_and_process_data()
        
        # Аналіз даних
        stats, forecasts, comparison_data = analyze_data(processed_data, config)
        
        # Візуалізація даних
        if processed_data is not None:
            visualize_data(processed_data, forecasts, comparison_data, config)
        
        # Генерація звіту
        if stats is not None:
            generate_report(stats, config)
        
        logger.info("Проект успішно завершено")
        print("\nАналіз завершено. Результати збережено у директоріях:")
        print(f"- Графіки: {FIGURES_OUTPUT_DIR}")
        print("- Звіти: output/reports")
        
    except Exception as e:
        logger.error(f"Помилка при виконанні програми: {e}")
        print(f"Сталася помилка: {e}")
        sys.exit(1)
