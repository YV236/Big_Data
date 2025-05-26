# config.py

import os
import argparse
import json

# Basic settings
EXTERNAL_API_URL = "https://countriesnow.space/api/v0.1/countries/population"
DATABASE_PATH = "data/processed/population.db"
FIGURES_OUTPUT_DIR = "output/figures"
LOGGING_LEVEL = "INFO"
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
API_PORT = 5000
API_DEBUG = True

# Default values
DEFAULT_COUNTRIES_TO_ANALYZE = ["Ukraine", "Poland", "Germany", "France", "United Kingdom"]
DEFAULT_START_YEAR = 1960
DEFAULT_END_YEAR = 2018
DEFAULT_FORECAST_YEARS = 5

# Function to load user settings from file
def load_user_config(config_file="user_config.json"):
    """
    Loads user settings from JSON file.
    
    Args:
        config_file (str): Path to configuration file
    
    Returns:
        dict: User settings
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    return {}

# Function to save user settings to file
def save_user_config(config, config_file="user_config.json"):
    """
    Saves user settings to JSON file.
    
    Args:
        config (dict): User settings
        config_file (str): Path to configuration file
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving configuration: {e}")

# Function to get settings from command line arguments
def get_args():
    """
    Gets settings from command line arguments.
    
    Returns:
        argparse.Namespace: Object with arguments
    """
    parser = argparse.ArgumentParser(description='Population Analysis Project')
    
    parser.add_argument('--countries', nargs='+', help='List of countries for analysis')
    parser.add_argument('--start-year', type=int, help='Start year for analysis')
    parser.add_argument('--end-year', type=int, help='End year for analysis')
    parser.add_argument('--forecast-years', type=int, help='Number of years for forecasting')
    parser.add_argument('--save-config', action='store_true', help='Save settings to file')
    
    return parser.parse_args()

# Loading user settings
user_config = load_user_config()

# Getting settings from command line arguments
args = get_args()

# Combining settings with priority for command line arguments
COUNTRIES_TO_ANALYZE = args.countries or user_config.get('countries', DEFAULT_COUNTRIES_TO_ANALYZE)
START_YEAR = args.start_year or user_config.get('start_year', DEFAULT_START_YEAR)
END_YEAR = args.end_year or user_config.get('end_year', DEFAULT_END_YEAR)
FORECAST_YEARS = args.forecast_years or user_config.get('forecast_years', DEFAULT_FORECAST_YEARS)

# Save settings if specified
if args.save_config:
    config_to_save = {
        'countries': COUNTRIES_TO_ANALYZE,
        'start_year': START_YEAR,
        'end_year': END_YEAR,
        'forecast_years': FORECAST_YEARS
    }
    save_user_config(config_to_save)

# Function for interactive parameter selection
def interactive_config():
    """
    Allows user to interactively select analysis parameters.
    
    Returns:
        dict: User-selected parameters
    """
    print("=== Population Analysis Configuration ===")
    
    # Country selection
    print(f"Current country list: {', '.join(COUNTRIES_TO_ANALYZE)}")
    change_countries = input("Do you want to change the country list? (y/n): ").lower() == 'y'
    
    countries = COUNTRIES_TO_ANALYZE
    if change_countries:
        countries_input = input("Enter countries separated by commas: ")
        countries = [country.strip() for country in countries_input.split(',')]
    
    # Years selection
    print(f"Current country list: {', '.join(COUNTRIES_TO_ANALYZE)}")
    change_years = input("Do you want to change the country list? (y/n): ").lower() == 'y'
    
    start_year = START_YEAR
    end_year = END_YEAR
    if change_years:
        start_year = int(input(f"Enter start year (min. {DEFAULT_START_YEAR}): ") or START_YEAR)
        end_year = int(input(f"Enter end year (max. {DEFAULT_END_YEAR}): ") or END_YEAR)
    
    # Forecast years selection
    print(f"Current number of years for forecasting: {FORECAST_YEARS}")
    change_forecast = input("Do you want to change the number of years for forecasting? (y/n): ").lower() == 'y'
    
    forecast_years = FORECAST_YEARS
    if change_forecast:
        forecast_years = int(input("Enter number of years for forecasting: ") or FORECAST_YEARS)
    
    # Save settings
    save_config = input("Save these settings for future runs? (y/n): ").lower() == 'y'
    
    config = {
        'countries': countries,
        'start_year': start_year,
        'end_year': end_year,
        'forecast_years': forecast_years
    }
    
    if save_config:
        save_user_config(config)
    
    return config

# Function to get current settings
def get_config(interactive=False):
    """
    Returns current settings or asks user for them.
    
    Args:
        interactive (bool): Whether to ask for settings interactively
    
    Returns:
        dict: Settings for analysis
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
