import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging
from datetime import datetime

class DataVisualizer:
    """
    Class for visualizing population data.
    """
    
    def __init__(self, output_dir="output/figures"):
        """
        Initialize the data visualizer.
        
        Args:
            output_dir (str): Directory to save the charts
        """
        self.output_dir = output_dir
        
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Set plot style
        sns.set(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 12
    
    def plot_population_growth(self, df, country=None, start_year=None, end_year=None, save=True, show=True):
        """
        Plot population growth chart.

        Args:
            df (pandas.DataFrame): Data for visualization
            country (str, optional): Country name. If not provided, plots for all countries.
            start_year (int, optional): Start year
            end_year (int, optional): End year
            save (bool): Save chart to file
            show (bool): Show chart

        Returns:
            str: Path to saved file (if save=True)
        """
        self.logger.info("Plotting population growth chart")

        try:
            plt.figure(figsize=(12, 6))

            # Filter by years
            if start_year is not None:
                df = df[df['year'] >= start_year]
            if end_year is not None:
                df = df[df['year'] <= end_year]

            if country:
                # Filter data for the specified country
                country_data = df[df['country'] == country]

                if country_data.empty:
                    self.logger.warning(f"No data for country {country}")
                    return None

                # Plot for a single country
                plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2)
                plt.title(f'Population growth: {country}')
            else:
                # Select top-5 countries by population in the latest year
                latest_year = df['year'].max()
                top_countries = df[df['year'] == latest_year].nlargest(5, 'value')['country'].unique()

                # Plot for each country
                for country in top_countries:
                    country_data = df[df['country'] == country]
                    plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2, label=country)

                plt.legend()
                top_countries_str = ', '.join(top_countries)
                plt.title(f"Population growth: Top-5 countries ({top_countries_str})")

            plt.xlabel('Year')
            plt.ylabel('Population')
            plt.grid(True)

            # Save chart
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                country_suffix = f"_{country}" if country else "_top5"
                filename = f"population_growth{country_suffix}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)

                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Chart saved to file {filepath}")

            # Show chart
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Error while plotting population growth chart: {e}")
            plt.close()
            raise
    
    def plot_growth_percentage(self, df, country=None, start_year=None, end_year=None, save=True, show=True):
        """
        Plot population growth percentage chart.

        Args:
            df (pandas.DataFrame): Data for visualization
            country (str, optional): Country name. If not provided, plots for all countries.
            start_year (int, optional): Start year
            end_year (int, optional): End year
            save (bool): Save chart to file
            show (bool): Show chart

        Returns:
            str: Path to saved file (if save=True)
        """
        self.logger.info("Plotting population growth percentage chart")

        try:
            plt.figure(figsize=(12, 6))

            # Filter by years
            if start_year is not None:
                df = df[df['year'] >= start_year]
            if end_year is not None:
                df = df[df['year'] <= end_year]

            if country:
                # Filter data for the specified country
                country_data = df[df['country'] == country].dropna(subset=['growth_percentage'])

                if country_data.empty:
                    self.logger.warning(f"No data for country {country}")
                    return None

                # Plot for a single country
                plt.bar(country_data['year'], country_data['growth_percentage'], color='skyblue')
                plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
                plt.title(f'Population growth percentage: {country}')
            else:
                # Calculate average growth percentage per year
                yearly_avg = df.groupby('year')['growth_percentage'].mean().reset_index()

                # Plot average growth percentage
                plt.bar(yearly_avg['year'], yearly_avg['growth_percentage'], color='skyblue')
                plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
                plt.title('Average population growth percentage by year')
            
            plt.xlabel('Year')
            plt.ylabel('Growth percentage (%)')
            plt.grid(axis='y')
            
            # Save chart
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                country_suffix = f"_{country}" if country else "_avg"
                filename = f"growth_percentage{country_suffix}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Chart saved to file {filepath}")
            
            # Show chart
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Error while plotting population growth percentage chart: {e}")
            plt.close()
            raise
    
    def plot_population_comparison(self, df, countries, start_year=None, end_year=None, save=True, show=True):
        """
        Plot population comparison chart for selected countries.

        Args:
            df (pandas.DataFrame): Data for visualization
            countries (list): List of countries to compare
            start_year (int, optional): Start year
            end_year (int, optional): End year
            save (bool): Save chart to file
            show (bool): Show chart

        Returns:
            str: Path to saved file (if save=True)
        """
        self.logger.info(f"Plotting population comparison chart for countries: {', '.join(countries)}")

        try:
            # Filter data by countries
            filtered_df = df[df['country'].isin(countries)]

            if filtered_df.empty:
                self.logger.warning("No data for selected countries")
                return None

            # Filter by years, if provided
            if start_year is not None:
                filtered_df = filtered_df[filtered_df['year'] >= start_year]

            if end_year is not None:
                filtered_df = filtered_df[filtered_df['year'] <= end_year]

            plt.figure(figsize=(12, 6))

            # Plot for each country
            for country in countries:
                country_data = filtered_df[filtered_df['country'] == country]
                if not country_data.empty:
                    plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2, label=country)

            plt.title('Country population comparison')
            plt.xlabel('Year')
            plt.ylabel('Population')
            plt.legend()
            plt.grid(True)

            # Save chart
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"population_comparison_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Chart saved to file {filepath}")
            
            # Show chart
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Error while plotting population comparison chart: {e}")
            plt.close()
            raise
    
    def plot_population_forecast(self, actual_df, forecast_df, country, save=True, show=True):
        """
        Plot population forecast chart.

        Args:
            actual_df (pandas.DataFrame): Actual data
            forecast_df (pandas.DataFrame): Forecasted data
            country (str): Country name
            save (bool): Save chart to file
            show (bool): Show chart

        Returns:
            str: Path to saved file (if save=True)
        """
        self.logger.info(f"Plotting population forecast chart for country {country}")

        try:
            plt.figure(figsize=(12, 6))

            # Plot actual data
            plt.plot(actual_df['year'], actual_df['value'], marker='o', linewidth=2, label='Actual data')

            # Plot forecasted data
            plt.plot(forecast_df['year'], forecast_df['value'], marker='s', linestyle='--', linewidth=2, label='Forecast')

            plt.title(f'Population forecast: {country}')
            plt.xlabel('Year')
            plt.ylabel('Population')
            plt.legend()
            plt.grid(True)

            # Save chart
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"population_forecast_{country}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Chart saved to file {filepath}")
            
            # Show chart
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Error while plotting population forecast chart: {e}")
            plt.close()
            raise
    
    def plot_heatmap(self, df, countries, start_year=None, end_year=None, save=True, show=True):
        """
        Plot heatmap of population growth percentage.

        Args:
            df (pandas.DataFrame): Data for visualization
            countries (list): List of countries
            start_year (int, optional): Start year
            end_year (int, optional): End year
            save (bool): Save chart to file
            show (bool): Show chart

        Returns:
            str: Path to saved file (if save=True)
        """
        self.logger.info("Plotting heatmap of population growth percentage")

        try:
            # Filter data by countries
            filtered_df = df[df['country'].isin(countries)]

            if filtered_df.empty:
                self.logger.warning("No data for selected countries")
                return None

            # Filter by years, if provided
            if start_year is not None:
                filtered_df = filtered_df[filtered_df['year'] >= start_year]

            if end_year is not None:
                filtered_df = filtered_df[filtered_df['year'] <= end_year]

            # Prepare data for heatmap
            pivot_df = filtered_df.pivot_table(index='country', columns='year', values='growth_percentage')
            
            plt.figure(figsize=(14, 8))
            
            # Plot heatmap
            sns.heatmap(pivot_df, annot=True, cmap='coolwarm', center=0, fmt='.1f')
            
            plt.title('Heatmap of population growth percentage')
            plt.xlabel('Year')
            plt.ylabel('Country')
            
            # Save chart
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"growth_heatmap_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Chart saved to file {filepath}")
            
            # Show chart
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Error while plotting heatmap: {e}")
            plt.close()
            raise
