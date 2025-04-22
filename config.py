# config.py

import os
import argparse
import json

# Базові налаштування
EXTERNAL_API_URL = "https://countriesnow.space/api/v0.1/countries/population"
DATABASE_PATH = "data/processed/population.db"
FIGURES_OUTPUT_DIR = "output/figures"
LOGGING_LEVEL = "INFO"
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
API_PORT = 5000
API_DEBUG = True

# Значення за замовчуванням
DEFAULT_COUNTRIES_TO_ANALYZE = ["Ukraine", "Poland", "Germany", "France", "United Kingdom"]
DEFAULT_START_YEAR = 1960
DEFAULT_END_YEAR = 2018
DEFAULT_FORECAST_YEARS = 5

# Функція для завантаження користувацьких налаштувань з файлу
def load_user_config(config_file="user_config.json"):
    """
    Завантажує користувацькі налаштування з JSON файлу.
    
    Args:
        config_file (str): Шлях до файлу конфігурації
    
    Returns:
        dict: Користувацькі налаштування
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Помилка при завантаженні конфігурації: {e}")
    return {}

# Функція для збереження користувацьких налаштувань у файл
def save_user_config(config, config_file="user_config.json"):
    """
    Зберігає користувацькі налаштування у JSON файл.
    
    Args:
        config (dict): Користувацькі налаштування
        config_file (str): Шлях до файлу конфігурації
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Помилка при збереженні конфігурації: {e}")

# Функція для отримання налаштувань з аргументів командного рядка
def get_args():
    """
    Отримує налаштування з аргументів командного рядка.
    
    Returns:
        argparse.Namespace: Об'єкт з аргументами
    """
    parser = argparse.ArgumentParser(description='Population Analysis Project')
    
    parser.add_argument('--countries', nargs='+', help='Список країн для аналізу')
    parser.add_argument('--start-year', type=int, help='Початковий рік для аналізу')
    parser.add_argument('--end-year', type=int, help='Кінцевий рік для аналізу')
    parser.add_argument('--forecast-years', type=int, help='Кількість років для прогнозування')
    parser.add_argument('--save-config', action='store_true', help='Зберегти налаштування у файл')
    
    return parser.parse_args()

# Завантаження користувацьких налаштувань
user_config = load_user_config()

# Отримання налаштувань з аргументів командного рядка
args = get_args()

# Об'єднання налаштувань з пріоритетом для аргументів командного рядка
COUNTRIES_TO_ANALYZE = args.countries or user_config.get('countries', DEFAULT_COUNTRIES_TO_ANALYZE)
START_YEAR = args.start_year or user_config.get('start_year', DEFAULT_START_YEAR)
END_YEAR = args.end_year or user_config.get('end_year', DEFAULT_END_YEAR)
FORECAST_YEARS = args.forecast_years or user_config.get('forecast_years', DEFAULT_FORECAST_YEARS)

# Збереження налаштувань, якщо вказано
if args.save_config:
    config_to_save = {
        'countries': COUNTRIES_TO_ANALYZE,
        'start_year': START_YEAR,
        'end_year': END_YEAR,
        'forecast_years': FORECAST_YEARS
    }
    save_user_config(config_to_save)

# Функція для інтерактивного вибору параметрів
def interactive_config():
    """
    Дозволяє користувачу інтерактивно вибрати параметри аналізу.
    
    Returns:
        dict: Вибрані користувачем параметри
    """
    print("=== Налаштування аналізу населення ===")
    
    # Вибір країн
    print(f"Поточний список країн: {', '.join(COUNTRIES_TO_ANALYZE)}")
    change_countries = input("Бажаєте змінити список країн? (y/n): ").lower() == 'y'
    
    countries = COUNTRIES_TO_ANALYZE
    if change_countries:
        countries_input = input("Введіть країни через кому: ")
        countries = [country.strip() for country in countries_input.split(',')]
    
    # Вибір років
    print(f"Поточний діапазон років: {START_YEAR}-{END_YEAR}")
    change_years = input("Бажаєте змінити діапазон років? (y/n): ").lower() == 'y'
    
    start_year = START_YEAR
    end_year = END_YEAR
    if change_years:
        start_year = int(input(f"Введіть початковий рік (мін. {DEFAULT_START_YEAR}): ") or START_YEAR)
        end_year = int(input(f"Введіть кінцевий рік (макс. {DEFAULT_END_YEAR}): ") or END_YEAR)
    
    # Вибір років для прогнозування
    print(f"Поточна кількість років для прогнозування: {FORECAST_YEARS}")
    change_forecast = input("Бажаєте змінити кількість років для прогнозування? (y/n): ").lower() == 'y'
    
    forecast_years = FORECAST_YEARS
    if change_forecast:
        forecast_years = int(input("Введіть кількість років для прогнозування: ") or FORECAST_YEARS)
    
    # Збереження налаштувань
    save_config = input("Зберегти ці налаштування для майбутніх запусків? (y/n): ").lower() == 'y'
    
    config = {
        'countries': countries,
        'start_year': start_year,
        'end_year': end_year,
        'forecast_years': forecast_years
    }
    
    if save_config:
        save_user_config(config)
    
    return config

# Функція для отримання поточних налаштувань
def get_config(interactive=False):
    """
    Повертає поточні налаштування або запитує їх у користувача.
    
    Args:
        interactive (bool): Чи запитувати налаштування інтерактивно
    
    Returns:
        dict: Налаштування для аналізу
    """
    if interactive:
        return interactive_config()
    else:
        return {
            'countries': COUNTRIES_TO_ANALYZE,
            'start_year': START_YEAR,
            'end_year': END_YEAR,
            'forecast_years': FORECAST_YEARS
        }
