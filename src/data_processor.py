import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime

class DataProcessor:
    """
    Class for processing and transforming population data.
    """
    
    def __init__(self, db_path="data/processed/population.db"):
        """
        Initialization of the data processor.
        
        Args:
            db_path (str): Path to SQLite database
        """
        self.db_path = db_path
        
        # Create directory for database if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_data(self, data):
        """
        Processing population data.
        
        Args:
            data (dict): Data in JSON format
        
        Returns:
            pandas.DataFrame: Processed data
        """
        self.logger.info("Starting data processing")
        
        try:
            # Converting data to DataFrame
            df = pd.json_normalize(data['data'])
            
            # Expanding populationCounts list
            df_expanded = df.explode('populationCounts')
            df_expanded = pd.concat([
                df_expanded.drop(['populationCounts'], axis=1),
                df_expanded['populationCounts'].apply(pd.Series)
            ], axis=1)
            
            # Calculating population growth percentage
            df_expanded = df_expanded.sort_values(['country', 'year'])
            df_expanded['growth_value'] = df_expanded.groupby('country')['value'].diff()
            df_expanded['growth_percentage'] = df_expanded.groupby('country')['value'].pct_change() * 100
            
            self.logger.info("Data successfully processed")
            return df_expanded
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise
    
    def save_to_database(self, df):
        """
        Saving data to SQLite database.
        
        Args:
            df (pandas.DataFrame): Data to save
        """
        self.logger.info(f"Saving data to database {self.db_path}")
        
        try:
            # Connecting to database
            conn = sqlite3.connect(self.db_path)
            
            # Saving data to table
            df.to_sql('population', conn, if_exists='replace', index=False)
            
            # Creating indexes to speed up queries
            cursor = conn.cursor()
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON population (country)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON population (year)')
            conn.commit()
            
            # Closing connection
            conn.close()
            
            self.logger.info("Data successfully saved to database")
        except Exception as e:
            self.logger.error(f"Error saving data to database: {e}")
            raise
    
    def load_from_database(self, query=None):
        """
        Loading data from SQLite database.
        
        Args:
            query (str, optional): SQL query. If not specified, all data from population table is loaded.
        
        Returns:
            pandas.DataFrame: Loaded data
        """
        self.logger.info(f"Loading data from database {self.db_path}")
        
        try:
            # Executing query
            conn = sqlite3.connect(self.db_path)
            
            # Executing query
            if query is None:
                query = "SELECT * FROM population"
            
            df = pd.read_sql_query(query, conn)
            
            # Closing connection
            conn.close()
            
            self.logger.info("Data successfully loaded from database")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data from database: {e}")
            raise
    
    def export_to_csv(df, filename="population_data.csv"):
        """
        Exports DataFrame to a CSV file in the output/csv directory.
        
        Args:
        df (pandas.DataFrame): Data to export
        filename (str): File name
        """
        output_dir = "output/csv"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Data saved to CSV file: {filepath}")
    
    def export_to_excel(df, filename="population_data.xlsx"):
        """
        Exports DataFrame to an Excel file in the output/excel directory.
        
        Args:
        df (pandas.DataFrame): Data for export
        filename (str): File name
        """
        output_dir = "output/excel"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False, sheet_name='Population Data')
        print(f"Data saved to Excel file: {filepath}")
        
    def export_to_json(df, filename="population_data.json", orient="records"):
        """
        Exports DataFrame to a JSON file in the output/json directory.
        
        Args:
        df (pandas.DataFrame): Дані для експорту
        filename (str): Назва файлу
        orient (str): JSON orientation ('records', 'split', 'index', 'columns', 'values')
        """
        output_dir = "output/json"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_json(filepath, orient=orient)
        print(f"Data saved to JSON file: {filepath}")
