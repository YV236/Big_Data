import requests
import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class DataAnalyzer:
    """
    Клас для аналізу даних про населення.
    """
    
    def __init__(self):
        """
        Ініціалізація аналізатора даних.
        """
        # Налаштування логування
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def calculate_statistics(self, df):
        """
        Розрахунок статистичних показників.
        
        Args:
            df (pandas.DataFrame): Дані для аналізу
        
        Returns:
            dict: Статистичні показники
        """
        self.logger.info("Розрахунок статистичних показників")
        
        try:
            stats = {}
            
            # Загальна статистика
            stats['total_countries'] = df['country'].nunique()
            stats['year_range'] = (df['year'].min(), df['year'].max())
            
            # Статистика по населенню
            stats['total_population_start'] = df[df['year'] == df['year'].min()]['value'].sum()
            stats['total_population_end'] = df[df['year'] == df['year'].max()]['value'].sum()
            stats['total_growth_percentage'] = (
                (stats['total_population_end'] - stats['total_population_start']) / 
                stats['total_population_start'] * 100
            )
            
            # Середній щорічний приріст
            stats['avg_annual_growth_percentage'] = df.groupby('year')['growth_percentage'].mean().mean()
            
            # Країни з найбільшим та найменшим населенням
            latest_year = df['year'].max()
            latest_data = df[df['year'] == latest_year]
            
            stats['largest_population_country'] = latest_data.loc[latest_data['value'].idxmax()]['country']
            stats['largest_population_value'] = latest_data['value'].max()
            
            stats['smallest_population_country'] = latest_data.loc[latest_data['value'].idxmin()]['country']
            stats['smallest_population_value'] = latest_data['value'].min()
            
            # Країни з найбільшим та найменшим приростом
            growth_data = df.groupby('country').apply(
                lambda x: ((x[x['year'] == x['year'].max()]['value'].values[0] - 
                           x[x['year'] == x['year'].min()]['value'].values[0]) / 
                           x[x['year'] == x['year'].min()]['value'].values[0] * 100)
            ).reset_index(name='total_growth_pct')
            
            stats['highest_growth_country'] = growth_data.loc[growth_data['total_growth_pct'].idxmax()]['country']
            stats['highest_growth_percentage'] = growth_data['total_growth_pct'].max()
            
            stats['lowest_growth_country'] = growth_data.loc[growth_data['total_growth_pct'].idxmin()]['country']
            stats['lowest_growth_percentage'] = growth_data['total_growth_pct'].min()
            
            self.logger.info("Статистичні показники успішно розраховані")
            return stats
        except Exception as e:
            self.logger.error(f"Помилка при розрахунку статистичних показників: {e}")
            raise
    
    def predict_population(self, df, country, years_to_predict=5):
        """
        Прогнозування населення на майбутні роки.
        
        Args:
            df (pandas.DataFrame): Дані для аналізу
            country (str): Назва країни
            years_to_predict (int): Кількість років для прогнозування
        
        Returns:
            pandas.DataFrame: Дані з прогнозом
        """
        self.logger.info(f"Прогнозування населення для країни {country} на {years_to_predict} років")
        
        try:
            # Фільтрація даних для вказаної країни
            country_data = df[df['country'] == country].sort_values('year')
            
            if country_data.empty:
                self.logger.warning(f"Немає даних для країни {country}")
                return None
            
            # Підготовка даних для моделі
            X = country_data[['year']].values
            y = country_data['value'].values
            
            # Створення та навчання моделі
            model = LinearRegression()
            model.fit(X, y)
            
            # Оцінка якості моделі
            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            self.logger.info(f"Модель навчена: MSE = {mse}, R² = {r2}")
            
            # Прогнозування на майбутні роки
            last_year = country_data['year'].max()
            future_years = np.array([[year] for year in range(last_year + 1, last_year + years_to_predict + 1)])
            future_population = model.predict(future_years)
            
            # Створення DataFrame з прогнозом
            future_df = pd.DataFrame({
                'country': country,
                'year': future_years.flatten(),
                'value': future_population,
                'is_predicted': True
            })
            
            # Додавання ознаки is_predicted до оригінальних даних
            country_data['is_predicted'] = False
            
            # Об'єднання оригінальних даних з прогнозом
            result_df = pd.concat([country_data, future_df], ignore_index=True)
            
            self.logger.info("Прогноз успішно створено")
            return result_df
        except Exception as e:
            self.logger.error(f"Помилка при прогнозуванні населення: {e}")
            raise
    
    def compare_countries(self, df, countries, start_year=None, end_year=None):
        """
        Порівняння населення різних країн.

        Args:
            df (pandas.DataFrame): Дані для аналізу
            countries (list): Список країн для порівняння
            start_year (int, optional): Початковий рік
            end_year (int, optional): Кінцевий рік

        Returns:
            pandas.DataFrame: Дані для порівняння
        """
    self.logger.info(f"Порівняння країн: {', '.join(countries)}")

    try:
        # Фільтрація даних за країнами
        filtered_df = df[df['country'].isin(countries)]

        if filtered_df.empty:
            self.logger.warning("Немає даних для вказаних країн")
            return None

        # Фільтрація за роками, якщо вказано
        if start_year is not None:
            filtered_df = filtered_df[filtered_df['year'] >= start_year]

        if end_year is not None:
            filtered_df = filtered_df[filtered_df['year'] <= end_year]

        # Розрахунок загального приросту для країн
        filtered_df = filtered_df.sort_values(['country', 'year'])
        filtered_df['growth_value'] = filtered_df.groupby('country')['value'].diff()
        filtered_df['growth_percentage'] = filtered_df.groupby('country')['value'].pct_change() * 100

        return filtered_df

    except Exception as e:
        self.logger.error(f"Помилка при порівнянні країн: {e}")
        return None
