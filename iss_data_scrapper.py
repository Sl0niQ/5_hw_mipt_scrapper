#python
#environment: scrapperenv
#iss_data_scrapper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, strftime
import os
import csv
import threading
from config import FILE_PATH, CSV_SEPARATOR, BUFFER_SIZE

class ISSBrowser:
    """Эмуляция браузера, парсинг данных"""

    def __init__(self):
        self.driver = None
    
    def setup_browser(self):
        """Настройка браузера"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def load_iss_tracker(self):
        """Загрузка трекера МКС"""
        print("Подключение к сайту NASA")        
        self.driver.get("https://www.nasa.gov/spot-the-station/")
        
        print("Поиск фрейма с телеметрией МКС")
        iframe = self.driver.find_element(
            By.XPATH, "//iframe[@src='https://isstracker.spaceflight.esa.int/index.php']"
        )
        self.driver.switch_to.frame(iframe)
        
        print("Ожидание загрузки данных")
        wait = WebDriverWait(self.driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id='isst_dt_data']")))
    
    def get_iss_data(self):
        """Парсинг данных МКС"""
        return {
            'lat': self.driver.find_element(By.ID, "isst_lat").text,
            'lon': self.driver.find_element(By.ID, "isst_lon").text,
            'alt': self.driver.find_element(By.ID, "isst_alt").text,
            'spd': self.driver.find_element(By.ID, "isst_spd").text
        }
    
    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.switch_to.default_content()
            self.driver.quit()

class DataWriter:
    """Работа с данными, запись в файл"""

    def __init__(self):
        self.data_buffer = []
        self.buffer_count = 0
        self.file = None
        self.writer = None
    
    def initialize_file(self):
        """Инициализация файла данных"""        
        self.file = open(FILE_PATH, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file, delimiter=CSV_SEPARATOR)
        
        if not os.path.isfile(FILE_PATH) or os.path.getsize(FILE_PATH) == 0:
            self.add_data(['date', 'lat', 'lon', 'alt', 'speed'])
    
    def add_data(self, data_row):
        """Добавление данных в буфер"""
        self.data_buffer.append(data_row)
        self.buffer_count += 1
        
        if self.buffer_count >= BUFFER_SIZE:
            self.flush_buffer()
    
    def flush_buffer(self):
        """Запись буфера в файл"""
        if self.data_buffer:
            self.writer.writerows(self.data_buffer)
            self.file.flush()
            self.data_buffer = []
            self.buffer_count = 0
    
    def close(self):
        """Закрытие файла"""
        if self.file:
            self.flush_buffer()
            self.file.close()

class ISSCollectorApp:
    """Координатор работы скраппера"""

    def __init__(self):
        self.stop_flag = False
        self.browser = ISSBrowser()
        self.writer = DataWriter()
    
    def wait_for_exit(self):
        """Фоновый поток для команды exit"""
        while not self.stop_flag:
            if input().strip().lower() == 'exit':
                print("Завершение работы...")
                self.stop_flag = True
                break
    
    def run(self):
        """Главный цикл сбора данных"""
        try:
            # Инициализация
            self.browser.setup_browser()
            self.writer.initialize_file()
            
            # Запуск фонового потока
            exit_thread = threading.Thread(target=self.wait_for_exit, daemon=True)
            exit_thread.start()
            
            # Загрузка трекера            
            self.browser.load_iss_tracker()
            
            # Главный цикл            
            self._main_loop()
            
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.cleanup()
    
    def _main_loop(self):
        """Основной цикл сбора данных"""
        print(f"Сбор данных\nДля выхода введите 'exit' и нажмите 'Enter'\n")
        print(f"{'дата':20} {'широта':10} {'долгота':10} {'высота':8} {'скорость':10}") 
        while not self.stop_flag:
            try:
                # Получение данных
                iss_data = self.browser.get_iss_data()
                timestamp = strftime("%Y-%m-%d %H:%M:%S")
                
                # Запись данных
                data_row = [timestamp, iss_data['lat'], iss_data['lon'], iss_data['alt'], iss_data['spd']]
                self.writer.add_data(data_row)
                
                # Логирование
                print(f"{timestamp:20} {iss_data['lat']:10} {iss_data['lon']:10} "
                      f"{iss_data['alt']:8} {iss_data['spd']:10}")
                
                # Ожидание
                self._wait_interval(45)
                
            except Exception as e:
                print(f"Ошибка в цикле: {e}")
                break
    
    def _wait_interval(self, seconds):
        """Ожидание между замерами"""
        for _ in range(seconds):
            if self.stop_flag:
                break
            sleep(1)
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.writer.close()
        self.browser.close()

if __name__ == "__main__":
    app = ISSCollectorApp()
    app.run()