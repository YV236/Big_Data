import requests
import json
import os
import logging
from datetime import datetime

class DataLoader:
    """
    Клас для завантаження даних про населення з API.
    """
    
    def __init__(self, api_url, output_dir="data/raw"):
        """
        Ініціалізація завантажувача даних.
        
        Args:
            api_url (str): URL API для отримання даних
            output_dir (str): Директорія для зберігання завантажених даних
        """
        self.api_url = api_url
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
    
    def fetch_data(self):
        """
        Завантаження даних з API.
        
        Returns:
            dict: Дані у форматі JSON
        """
        self.logger.info(f"Завантаження даних з {self.api_url}")
        
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Перевірка на помилки HTTP
            data = response.json()
            
            self.logger.info("Дані успішно завантажені")
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Помилка при завантаженні даних: {e}")
            raise
    
    def save_data(self, data, filename=None):
        """
        Збереження даних у файл JSON.
        
        Args:
            data (dict): Дані для збереження
            filename (str, optional): Ім'я файлу. Якщо не вказано, 
                                      використовується поточна дата і час.
        
        Returns:
            str: Шлях до збереженого файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"population_data_{timestamp}.json"
        
        file_path = os.path.join(self.output_dir, filename)
        
        self.logger.info(f"Збереження даних у файл {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            self.logger.info("Дані успішно збережені")
            return file_path
        except IOError as e:
            self.logger.error(f"Помилка при збереженні даних: {e}")
            raise
    
    def load_from_file(self, file_path):
        """
        Завантаження даних з файлу JSON.
        
        Args:
            file_path (str): Шлях до файлу
        
        Returns:
            dict: Дані у форматі JSON
        """
        self.logger.info(f"Завантаження даних з файлу {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info("Дані успішно завантажені з файлу")
            return data
        except IOError as e:
            self.logger.error(f"Помилка при завантаженні даних з файлу: {e}")
            raise
