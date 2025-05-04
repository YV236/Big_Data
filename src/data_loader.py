import requests
import json
import os
import logging
import glob
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
        os.makedirs(output_dir, exist_ok=True)
        
        # Налаштування логування
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_data(self, filename="population_data.json"):
        """
        Завантаження даних з API або з файлу.
        """
        # Sprawdź, czy існує JAKIKOLWIEK файл .json в каталозі raw
        existing_jsons = glob.glob(os.path.join(self.output_dir, "*.json"))
        if existing_jsons:
            # Якщо є принаймні один файл, використовуйте перший з них
            filepath = existing_jsons[0]
            self.logger.info(f"Завантаження даних з файлу {filepath}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except IOError as e:
                self.logger.error(f"Помилка при завантаженні даних з файлу: {e}")
                raise
        else:
            # Якщо немає жодного файлу, завантажте та збережіть
            filepath = os.path.join(self.output_dir, filename)
            self.logger.info(f"Завантаження даних з API {self.api_url}")
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)
            self.logger.info(f"Дані збережено у файл {filepath}")
            return data
    
    def save_data(self, data, filename="population_data.json"):
        """
        Zapisuje dane do pliku JSON (nadpisuje plik, nie tworzy nowego!).
        """
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
