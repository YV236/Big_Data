import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime

class DataProcessor:
    """
    Клас для обробки та перетворення даних про населення.
    """
    
    def __init__(self, db_path="data/processed/population.db"):
        """
        Ініціалізація обробника даних.
        
        Args:
            db_path (str): Шлях до бази даних SQLite
        """
        self.db_path = db_path
        
        # Створення директорії для бази даних, якщо вона не існує
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Налаштування логування
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_data(self, data):
        """
        Обробка даних про населення.
        
        Args:
            data (dict): Дані у форматі JSON
        
        Returns:
            pandas.DataFrame: Оброблені дані
        """
        self.logger.info("Початок обробки даних")
        
        try:
            # Перетворення даних у DataFrame
            df = pd.json_normalize(data['data'])
            
            # Розгортання списку populationCounts
            df_expanded = df.explode('populationCounts')
            df_expanded = pd.concat([
                df_expanded.drop(['populationCounts'], axis=1),
                df_expanded['populationCounts'].apply(pd.Series)
            ], axis=1)
            
            # Обчислення відсотка зростання населення
            df_expanded = df_expanded.sort_values(['country', 'year'])
            df_expanded['growth_value'] = df_expanded.groupby('country')['value'].diff()
            df_expanded['growth_percentage'] = df_expanded.groupby('country')['value'].pct_change() * 100
            
            self.logger.info("Дані успішно оброблені")
            return df_expanded
        except Exception as e:
            self.logger.error(f"Помилка при обробці даних: {e}")
            raise
    
    def save_to_database(self, df):
        """
        Збереження даних у базу даних SQLite.
        
        Args:
            df (pandas.DataFrame): Дані для збереження
        """
        self.logger.info(f"Збереження даних у базу даних {self.db_path}")
        
        try:
            # Підключення до бази даних
            conn = sqlite3.connect(self.db_path)
            
            # Збереження даних у таблицю
            df.to_sql('population', conn, if_exists='replace', index=False)
            
            # Створення індексів для прискорення запитів
            cursor = conn.cursor()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON population (country)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON population (year)')
            conn.commit()
            
            # Закриття з'єднання
            conn.close()
            
            self.logger.info("Дані успішно збережені у базу даних")
        except Exception as e:
            self.logger.error(f"Помилка при збереженні даних у базу даних: {e}")
            raise
    
    def load_from_database(self, query=None):
        """
        Завантаження даних з бази даних SQLite.
        
        Args:
            query (str, optional): SQL-запит. Якщо не вказано, 
                                   завантажуються всі дані з таблиці population.
        
        Returns:
            pandas.DataFrame: Завантажені дані
        """
        self.logger.info(f"Завантаження даних з бази даних {self.db_path}")
        
        try:
            # Підключення до бази даних
            conn = sqlite3.connect(self.db_path)
            
            # Виконання запиту
            if query is None:
                query = "SELECT * FROM population"
            
            df = pd.read_sql_query(query, conn)
            
            # Закриття з'єднання
            conn.close()
            
            self.logger.info("Дані успішно завантажені з бази даних")
            return df
        except Exception as e:
            self.logger.error(f"Помилка при завантаженні даних з бази даних: {e}")
            raise
    
    def export_to_csv(df, filename="population_data.csv"):
        """
        Експортує DataFrame у файл CSV в каталозі output/csv.
        
        Args:
        df (pandas.DataFrame): Дані для експорту
        filename (str): Назва файлу
        """
        output_dir = "output/csv"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Дані збережено у файл CSV: {filepath}")
    
    def export_to_excel(df, filename="population_data.xlsx"):
        """
        Експортує DataFrame у файл Excel в каталозі output/excel.
        
        Args:
        df (pandas.DataFrame): Дані для експорту
        filename (str): Назва файлу
        """
        output_dir = "output/excel"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False, sheet_name='Population Data')
        print(f"Дані збережено у файл Excel: {filepath}")
        
    def export_to_json(df, filename="population_data.json", orient="records"):
        """
        Експортує DataFrame у файл JSON в каталозі output/json.
        
        Args:
        df (pandas.DataFrame): Дані для експорту
        filename (str): Назва файлу
        orient (str): Орієнтація JSON ('records', 'split', 'index', 'columns', 'values')
        """
        output_dir = "output/json"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_json(filepath, orient=orient)
        print(f"Дані збережено у файл JSON: {filepath}")
