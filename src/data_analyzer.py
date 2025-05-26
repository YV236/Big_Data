import requests
import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class DataAnalyzer:
    """
    Class for population data analysis.
    """
    
    def __init__(self):
        """
        Initialization of the data analyzer.
        """
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def calculate_statistics(self, df):
        """
        Calculation of statistical indicators.
        
        Args:
            df (pandas.DataFrame): Data for analysis
        
        Returns:
            dict: Statistical indicators
        """
        self.logger.info("Calculating statistical indicators")
        
        try:
            stats = {}
            
            # General statistics
            stats['total_countries'] = df['country'].nunique()
            stats['year_range'] = (df['year'].min(), df['year'].max())
            
            # Population statistics
            stats['total_population_start'] = df[df['year'] == df['year'].min()]['value'].sum()
            stats['total_population_end'] = df[df['year'] == df['year'].max()]['value'].sum()
            stats['total_growth_percentage'] = (
                (stats['total_population_end'] - stats['total_population_start']) / 
                stats['total_population_start'] * 100
            )
            
            # Average annual growth
            stats['avg_annual_growth_percentage'] = df.groupby('year')['growth_percentage'].mean().mean()
            
            # Countries with largest and smallest population
            latest_year = df['year'].max()
            latest_data = df[df['year'] == latest_year]
            
            stats['largest_population_country'] = latest_data.loc[latest_data['value'].idxmax()]['country']
            stats['largest_population_value'] = latest_data['value'].max()
            
            stats['smallest_population_country'] = latest_data.loc[latest_data['value'].idxmin()]['country']
            stats['smallest_population_value'] = latest_data['value'].min()
            
            # Countries with highest and lowest growth
            growth_data = df.groupby('country').apply(
                lambda x: ((x[x['year'] == x['year'].max()]['value'].values[0] - 
                           x[x['year'] == x['year'].min()]['value'].values[0]) / 
                           x[x['year'] == x['year'].min()]['value'].values[0] * 100)
            ).reset_index(name='total_growth_pct')
            
            stats['highest_growth_country'] = growth_data.loc[growth_data['total_growth_pct'].idxmax()]['country']
            stats['highest_growth_percentage'] = growth_data['total_growth_pct'].max()
            
            stats['lowest_growth_country'] = growth_data.loc[growth_data['total_growth_pct'].idxmin()]['country']
            stats['lowest_growth_percentage'] = growth_data['total_growth_pct'].min()
            
            self.logger.info("Statistical indicators successfully calculated")
            return stats
        except Exception as e:
            self.logger.error(f"Error calculating statistical indicators: {e}")
            raise
    
    def predict_population(self, df, country, years_to_predict=5):
        """
        Population forecasting for future years.
        
        Args:
            df (pandas.DataFrame): Data for analysis
            country (str): Country name
            years_to_predict (int): Number of years to predict
        
        Returns:
            pandas.DataFrame: Data with forecast
        """
        self.logger.info(f"Forecasting population for country {country} for {years_to_predict} years")
        
        try:
            # Filtering data for the specified country
            country_data = df[df['country'] == country].sort_values('year')
            
            if country_data.empty:
                self.logger.warning(f"No data for country {country}")
                return None
            
            #  Preparing data for the model
            X = country_data[['year']].values
            y = country_data['value'].values
            
            # Creating and training the model
            model = LinearRegression()
            model.fit(X, y)
            
            #  Model evaluation
            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            self.logger.info(f"Model trained: MSE = {mse}, R² = {r2}")
            
            # Forecasting for future years
            last_year = country_data['year'].max()
            future_years = np.array([[year] for year in range(last_year + 1, last_year + years_to_predict + 1)])
            future_population = model.predict(future_years)
            
            # Creating DataFrame with forecast
            future_df = pd.DataFrame({
                'country': country,
                'year': future_years.flatten(),
                'value': future_population,
                'is_predicted': True
            })
            
            # Adding is_predicted flag to original data
            country_data['is_predicted'] = False
            
            # Combining original data with forecast
            result_df = pd.concat([country_data, future_df], ignore_index=True)
            
            self.logger.info("Forecast successfully created")
            return result_df
        except Exception as e:
            self.logger.error(f"Error during population forecasting: {e}")
            raise
    
    def compare_countries(self, df, countries, start_year=None, end_year=None):
        """
        Comparison of population between different countries.

        Args:
            df (pandas.DataFrame): Data for analysis
            countries (list): List of countries for comparison
            start_year (int, optional): Start year
            end_year (int, optional): End year

        Returns:
            pandas.DataFrame: Data for comparison
        """
        self.logger.info(f"Comparing countries: {', '.join(countries)}")

        try:
            # Filtering data by countries
            filtered_df = df[df['country'].isin(countries)]

            if filtered_df.empty:
                self.logger.warning("No data for specified countries")
                return None

            # Filtering by years if specified
            if start_year is not None:
                filtered_df = filtered_df[filtered_df['year'] >= start_year]

            if end_year is not None:
                filtered_df = filtered_df[filtered_df['year'] <= end_year]

            # Calculating total growth for countries
            filtered_df = filtered_df.sort_values(['country', 'year'])
            filtered_df['growth_value'] = filtered_df.groupby('country')['value'].diff()
            filtered_df['growth_percentage'] = filtered_df.groupby('country')['value'].pct_change() * 100

            return filtered_df

        except Exception as e:
            self.logger.error(f"Error during country comparison: {e}")
            return None

