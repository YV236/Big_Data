import requests
import json
import os
import logging
import glob
from datetime import datetime

class DataLoader:
    """
    Class for loading population data from API.
    """
    
    def __init__(self, api_url, output_dir="data/raw"):
        """
        Initialization of the data loader.
        
        Args:
            api_url (str): API URL for getting data
            output_dir (str): Directory for storing downloaded data
        """
        self.api_url = api_url
        self.output_dir = output_dir
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_data(self, filename="population_data.json"):
        """
        Loading data from API or from file.
        """
        # Check if ANY .json file exists in the raw directory
        existing_jsons = glob.glob(os.path.join(self.output_dir, "*.json"))
        if existing_jsons:
            # If there's at least one file, use the first one
            filepath = existing_jsons[0]
            self.logger.info(f"Loading data from file {filepath}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except IOError as e:
                self.logger.error(f"Error loading data from file: {e}")
                raise
        else:
            # If no file exists, download and save
            filepath = os.path.join(self.output_dir, filename)
            self.logger.info(f"Loading data from API {self.api_url}")
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)
            self.logger.info(f"Data saved to file {filepath}")
            return data
    
    def save_data(self, data, filename="population_data.json"):
        """
        Saves data to JSON file (overwrites file, doesn't create new one!).
        """
        file_path = os.path.join(self.output_dir, filename)
        self.logger.info(f"Saving data to file {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.logger.info("Data successfully saved")
            return file_path
        except IOError as e:
            self.logger.error(f"Error saving data: {e}")
            raise
    
    def load_from_file(self, file_path):
        """
        Loading data from JSON file.
        
        Args:
            file_path (str): Path to file
        
        Returns:
            dict: Data in JSON format
        """
        self.logger.info(f"Loading data from file {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info("Data successfully loaded from file")
            return data
        except IOError as e:
            self.logger.error(f"Error loading data from file: {e}")
            raise
