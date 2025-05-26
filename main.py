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
from src.data_reporter import PDFReporter
from config import (
    get_config, EXTERNAL_API_URL, DATABASE_PATH, FIGURES_OUTPUT_DIR,
    LOGGING_LEVEL, LOGGING_FORMAT,
    DEFAULT_COUNTRIES_TO_ANALYZE, DEFAULT_START_YEAR, DEFAULT_END_YEAR, DEFAULT_FORECAST_YEARS
)

# Logging configuration
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL),
    format=LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

def setup_environment():
    """
    Creates necessary directories for the project.
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
    Loads and processes population data.
    
    Returns:
        pandas.DataFrame: Processed data
    """
    # Loading data
    logger.info("Loading data...")
    data_loader = DataLoader(EXTERNAL_API_URL)
    
    try:
        raw_data = data_loader.fetch_data()
        data_path = data_loader.save_data(raw_data)
        logger.info(f"Data saved to {data_path}")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        sys.exit(1)
    
    # Processing data
    logger.info("Processing data...")
    data_processor = DataProcessor(DATABASE_PATH)
    
    try:
        processed_data = data_processor.process_data(raw_data)
        data_processor.save_to_database(processed_data)
        logger.info(f"Data processed and saved to database {DATABASE_PATH}")
        return processed_data
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        sys.exit(1)

def analyze_data(processed_data, config):
    """
    Analyzes population data.
    
    Args:
        processed_data (pandas.DataFrame): Processed data
        config (dict): Analysis configuration
    
    Returns:
        tuple: Statistics, forecasts and comparison data
    """
    logger.info("Analyzing data...")
    data_analyzer = DataAnalyzer()
    
    try:
        # Getting parameters from configuration
        countries = config['countries']
        start_year = config['start_year']
        end_year = config['end_year']
        forecast_years = config['forecast_years']
        
        # Calculating statistics
        stats = data_analyzer.calculate_statistics(processed_data)
        logger.info("Статистичні показники розраховано")
        
        # Population forecasting for selected countries
        forecasts = {}
        for country in countries:
            forecast = data_analyzer.predict_population(processed_data, country, forecast_years)
            if forecast is not None:
                forecasts[country] = forecast
        
        # Country comparison
        comparison_data = data_analyzer.compare_countries(
            processed_data, 
            countries, 
            start_year=start_year, 
            end_year=end_year
        )
        
        return stats, forecasts, comparison_data
    except Exception as e:
        logger.error(f"Error during data analysis: {e}")
        return None, None, None

def visualize_data(processed_data, forecasts, comparison_data, config):
    """
    Creates population data visualizations.
    
    Args:
        processed_data (pandas.DataFrame): Analyzed data
        forecasts (dict): Population forecasts
        comparison_data (pandas.DataFrame): Comparison data
        config (dict): Analysis configuration
    """
    logger.info("Data Visualization...")
    data_visualizer = DataVisualizer(FIGURES_OUTPUT_DIR)
    
    try:
        # Getting parameters from the configuration
        countries = config['countries']
        
        # Population growth chart for all countries
        data_visualizer.plot_population_growth(processed_data, country=None, start_year=config['start_year'], end_year=config['end_year'])
        data_visualizer.plot_growth_percentage(processed_data, country=None, start_year=config['start_year'], end_year=config['end_year'])
        
        # Population growth charts for each country separately
        for country in countries:
            country_data = processed_data[processed_data['country'] == country]
            if not country_data.empty:
                data_visualizer.plot_population_growth(country_data, country=country)
                data_visualizer.plot_growth_percentage(country_data, country=country)
        
        # Country comparison chart
        if comparison_data is not None:
            data_visualizer.plot_population_comparison(processed_data, countries, start_year=config['start_year'], end_year=config['end_year'])
        
        # Forecast charts
        for country, forecast_df in forecasts.items():
            actual_data = processed_data[processed_data['country'] == country]
            predicted_data = forecast_df[forecast_df['is_predicted'] == True]
            data_visualizer.plot_population_forecast(actual_data, predicted_data, country)
        
        # Growth heatmap
        data_visualizer.plot_heatmap(processed_data, countries, start_year=config['start_year'], end_year=config['end_year'])
        
        logger.info(f"Visualizations saved to directory {FIGURES_OUTPUT_DIR}")
    except Exception as e:
        logger.error(f"Error during data visualization: {e}")

def export_data_for_bi(processed_data, comparison_data, stats):
    """
    Exports data to various formats for BI tools integration
    
    Args:
        processed_data: DataFrame with processed data
        comparison_data: DataFrame with comparison data
        stats: DataFrame with statistics
    """
    # Export to CSV
    if processed_data is not None:
        DataProcessor.export_to_csv(processed_data, "processed_data.csv")
    if comparison_data is not None:
        DataProcessor.export_to_csv(comparison_data, "comparison_countries.csv")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_csv(stats.head(5), "top5_countries.csv")

    # Export to Excel (with correct extension!)
    if processed_data is not None:
        DataProcessor.export_to_excel(processed_data, "processed_data.xlsx")
    if comparison_data is not None:
        DataProcessor.export_to_excel(comparison_data, "comparison_countries.xlsx")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_excel(stats.head(5), "top5_countries.xlsx")
        
    # Export to JSON
    if processed_data is not None:
        DataProcessor.export_to_json(processed_data, "processed_data.json")
    if comparison_data is not None:
        DataProcessor.export_to_json(comparison_data, "comparison_countries.json")
    if stats is not None and hasattr(stats, 'head'):
        DataProcessor.export_to_json(stats.head(5), "top5_countries.json")
        
    print("Data successfully exported for BI tools integration")



def main():
    """
    Main function to run the Population Analysis project.
    """
    logger.info("Starting Population Analysis project")
    
    # Getting list of countries from API
    logger.info("Getting list of available countries...")
    try:
        response = requests.get(EXTERNAL_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # ...after getting data from API...
        raw_countries = [item['country'] for item in data['data']]
        # List of keywords that may indicate region/aggregate
        region_keywords = [
            "countries", "region", "income", "IDA", "IBRD", "aggregate", "total", "area", "Euro area"
        ]
        # Filtering only countries (without regions/aggregates)
        available_countries = [
            country for country in raw_countries
            if not any(keyword.lower() in country.lower() for keyword in region_keywords)
        ]
        
        # Displaying list of countries
        print("\nAvailable countries:")
        for i, country in enumerate(available_countries, 1):
            print(f"{i}. {country}")
            # Adding pause after every 20 countries for reading convenience
            if i % 20 == 0 and i < len(available_countries):
                input("Press Enter to continue...")
        
        # User country selection
        selected_countries = []
        while not selected_countries:
            print("\nSelect countries for analysis (enter numbers separated by commas):")
            country_indices = input("> ").strip().split(',')
            for idx in country_indices:
                try:
                    index = int(idx.strip()) - 1
                    if 0 <= index < len(available_countries):
                        selected_countries.append(available_countries[index])
                except ValueError:
                    pass
            if not selected_countries:
                print("No countries selected. Please try again.")

        # Start year selection
        while True:
            print("\nEnter start year (for example, 1960):")
            start_year_input = input("> ").strip()
            if start_year_input.isdigit():
                start_year = int(start_year_input)
                if 1960 <= start_year <= 2018:
                    break
                else:
                    print("Year must be between 1960-2018. Please try again.")
            else:
                print("Invalid value. Please try again.")

        # End year selection
        while True:
            print("\nEnter end year (for example, 2018):")
            end_year_input = input("> ").strip()
            if end_year_input.isdigit():
                end_year = int(end_year_input)
                if 1960 <= end_year <= 2018 and end_year >= start_year:
                    break
                elif end_year < start_year:
                    print("End year cannot be less than start year. Please try again.")
                else:
                    print("Year must be between 1960-2018. Please try again.")
            else:
                print("Invalid value. Please try again.")

        # Creating configuration based on user selection
        config = {
            'countries': selected_countries,
            'start_year': start_year,
            'end_year': end_year,
            'forecast_years': DEFAULT_FORECAST_YEARS
        }
        
        # Creating necessary directories
        setup_environment()
        
        # Cleaning figures folder
        clean_figures_folder()
        
        # Loading and processing data
        processed_data = load_and_process_data()
        
        # Data analysis
        stats, forecasts, comparison_data = analyze_data(processed_data, config)

        if processed_data is not None:
            export_data_for_bi(processed_data, comparison_data, stats)

        # Data visualization
        if processed_data is not None:
            visualize_data(processed_data, forecasts, comparison_data, config)

        # After data analysis
        if stats is not None:
            # Generating PDF reports
            PDFReporter.generate_pdf_report(processed_data, config, stats)
        
        logger.info("Project completed successfully")
        print("\nAnalysis completed. Results saved in directories:")
        print(f"- Figures: {FIGURES_OUTPUT_DIR}")
        print("- Reports: output/reports")
        
    except Exception as e:
        logger.error(f"Error during program execution: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()