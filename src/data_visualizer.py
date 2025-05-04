import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging
from datetime import datetime

class DataVisualizer:
    """
    Клас для візуалізації даних про населення.
    """
    
    def __init__(self, output_dir="output/figures"):
        """
        Ініціалізація візуалізатора даних.
        
        Args:
            output_dir (str): Директорія для збереження графіків
        """
        self.output_dir = output_dir
        
        # Створення директорії, якщо вона не існує
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Налаштування логування
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Налаштування стилю графіків
        sns.set(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 12
    
    def plot_population_growth(self, df, country=None, start_year=None, end_year=None, save=True, show=True):
        """
        Побудова графіка зростання населення.
        
        Args:
            df (pandas.DataFrame): Дані для візуалізації
            country (str, optional): Назва країни. Якщо не вказано, 
                                     будується графік для всіх країн.
            start_year (int, optional): Початковий рік
            end_year (int, optional): Кінцевий рік
            save (bool): Зберегти графік у файл
            show (bool): Показати графік
        
        Returns:
            str: Шлях до збереженого файлу (якщо save=True)
        """
        self.logger.info("Побудова графіка зростання населення")
        
        try:
            plt.figure(figsize=(12, 6))
            
            # Фільтрація за роками
            if start_year is not None:
                df = df[df['year'] >= start_year]
            if end_year is not None:
                df = df[df['year'] <= end_year]
            
            if country:
                # Фільтрація даних для вказаної країни
                country_data = df[df['country'] == country]
                
                if country_data.empty:
                    self.logger.warning(f"Немає даних для країни {country}")
                    return None
                
                # Побудова графіка для однієї країни
                plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2)
                plt.title(f'Зростання населення: {country}')
            else:
                # Вибір топ-5 країн за населенням у останньому році
                latest_year = df['year'].max()
                top_countries = df[df['year'] == latest_year].nlargest(5, 'value')['country'].unique()
                
                # Побудова графіків для кожної країни
                for country in top_countries:
                    country_data = df[df['country'] == country]
                    plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2, label=country)
                
                plt.legend()
                top_countries_str = ', '.join(top_countries)
                plt.title(f"Зростання населення: Топ-5 країн ({top_countries_str})")
            
            plt.xlabel('Рік')
            plt.ylabel('Населення')
            plt.grid(True)
            
            # Збереження графіка
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                country_suffix = f"_{country}" if country else "_top5"
                filename = f"population_growth{country_suffix}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Графік збережено у файл {filepath}")
            
            # Показ графіка
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Помилка при побудові графіка зростання населення: {e}")
            plt.close()
            raise
    
    def plot_growth_percentage(self, df, country=None, start_year=None, end_year=None, save=True, show=True):
        """
        Побудова графіка відсотка зростання населення.
        
        Args:
            df (pandas.DataFrame): Дані для візуалізації
            country (str, optional): Назва країни. Якщо не вказано, 
                                     будується графік для всіх країн.
            start_year (int, optional): Початковий рік
            end_year (int, optional): Кінцевий рік
            save (bool): Зберегти графік у файл
            show (bool): Показати графік
        
        Returns:
            str: Шлях до збереженого файлу (якщо save=True)
        """
        self.logger.info("Побудова графіка відсотка зростання населення")
        
        try:
            plt.figure(figsize=(12, 6))
            
            # Фільтрація за роками
            if start_year is not None:
                df = df[df['year'] >= start_year]
            if end_year is not None:
                df = df[df['year'] <= end_year]
            
            if country:
                # Фільтрація даних для вказаної країни
                country_data = df[df['country'] == country].dropna(subset=['growth_percentage'])
                
                if country_data.empty:
                    self.logger.warning(f"Немає даних для країни {country}")
                    return None
                
                # Побудова графіка для однієї країни
                plt.bar(country_data['year'], country_data['growth_percentage'], color='skyblue')
                plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
                plt.title(f'Відсоток зростання населення: {country}')
            else:
                # Розрахунок середнього відсотка зростання по роках
                yearly_avg = df.groupby('year')['growth_percentage'].mean().reset_index()
                
                # Побудова графіка середнього відсотка зростання
                plt.bar(yearly_avg['year'], yearly_avg['growth_percentage'], color='skyblue')
                plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
                plt.title('Середній відсоток зростання населення по роках')
            
            plt.xlabel('Рік')
            plt.ylabel('Відсоток зростання (%)')
            plt.grid(axis='y')
            
            # Збереження графіка
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                country_suffix = f"_{country}" if country else "_avg"
                filename = f"growth_percentage{country_suffix}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Графік збережено у файл {filepath}")
            
            # Показ графіка
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Помилка при побудові графіка відсотка зростання населення: {e}")
            plt.close()
            raise
    
    def plot_population_comparison(self, df, countries, start_year=None, end_year=None, save=True, show=True):
        """
        Побудова графіка порівняння населення різних країн.
        
        Args:
            df (pandas.DataFrame): Дані для візуалізації
            countries (list): Список країн для порівняння
            start_year (int, optional): Початковий рік
            end_year (int, optional): Кінцевий рік
            save (bool): Зберегти графік у файл
            show (bool): Показати графік
        
        Returns:
            str: Шлях до збереженого файлу (якщо save=True)
        """
        self.logger.info(f"Побудова графіка порівняння населення країн: {', '.join(countries)}")
        
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
            
            plt.figure(figsize=(12, 6))
            
            # Побудова графіків для кожної країни
            for country in countries:
                country_data = filtered_df[filtered_df['country'] == country]
                if not country_data.empty:
                    plt.plot(country_data['year'], country_data['value'], marker='o', linewidth=2, label=country)
            
            plt.title('Порівняння населення країн')
            plt.xlabel('Рік')
            plt.ylabel('Населення')
            plt.legend()
            plt.grid(True)
            
            # Збереження графіка
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"population_comparison_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Графік збережено у файл {filepath}")
            
            # Показ графіка
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Помилка при побудові графіка порівняння населення: {e}")
            plt.close()
            raise
    
    def plot_population_forecast(self, actual_df, forecast_df, country, save=True, show=True):
        """
        Побудова графіка прогнозу населення.
        
        Args:
            actual_df (pandas.DataFrame): Фактичні дані
            forecast_df (pandas.DataFrame): Прогнозовані дані
            country (str): Назва країни
            save (bool): Зберегти графік у файл
            show (bool): Показати графік
        
        Returns:
            str: Шлях до збереженого файлу (якщо save=True)
        """
        self.logger.info(f"Побудова графіка прогнозу населення для країни {country}")
        
        try:
            plt.figure(figsize=(12, 6))
            
            # Побудова графіка фактичних даних
            plt.plot(actual_df['year'], actual_df['value'], marker='o', linewidth=2, label='Фактичні дані')
            
            # Побудова графіка прогнозованих даних
            plt.plot(forecast_df['year'], forecast_df['value'], marker='s', linestyle='--', linewidth=2, label='Прогноз')
            
            plt.title(f'Прогноз населення: {country}')
            plt.xlabel('Рік')
            plt.ylabel('Населення')
            plt.legend()
            plt.grid(True)
            
            # Збереження графіка
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"population_forecast_{country}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Графік збережено у файл {filepath}")
            
            # Показ графіка
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Помилка при побудові графіка прогнозу населення: {e}")
            plt.close()
            raise
    
    def plot_heatmap(self, df, countries, start_year=None, end_year=None, save=True, show=True):
        """
        Побудова теплової карти зростання населення.
        
        Args:
            df (pandas.DataFrame): Дані для візуалізації
            countries (list): Список країн
            start_year (int, optional): Початковий рік
            end_year (int, optional): Кінцевий рік
            save (bool): Зберегти графік у файл
            show (bool): Показати графік
        
        Returns:
            str: Шлях до збереженого файлу (якщо save=True)
        """
        self.logger.info("Побудова теплової карти зростання населення")
        
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
            
            # Підготовка даних для теплової карти
            pivot_df = filtered_df.pivot_table(index='country', columns='year', values='growth_percentage')
            
            plt.figure(figsize=(14, 8))
            
            # Побудова теплової карти
            sns.heatmap(pivot_df, annot=True, cmap='coolwarm', center=0, fmt='.1f')
            
            plt.title('Теплова карта відсотка зростання населення')
            plt.xlabel('Рік')
            plt.ylabel('Країна')
            
            # Збереження графіка
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"growth_heatmap_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                self.logger.info(f"Графік збережено у файл {filepath}")
            
            # Показ графіка
            if show:
                plt.show()
            else:
                plt.close()
            
            return filepath if save else None
        except Exception as e:
            self.logger.error(f"Помилка при побудові теплової карти: {e}")
            plt.close()
            raise
