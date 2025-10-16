#venv: scrapperenv

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

stop_flag = False

def wait_for_exit():
	"""
	Обработчик команды остановки приложения
	"""
	global stop_flag    
	while not stop_flag:
		cmd = input().strip()
		if cmd.lower() == 'exit':
			print("Завершение работы")
			stop_flag = True
			break

file_path = 'iss_data.csv' # выходной файл для записи данных
BUFFER_SIZE = 50 # размер буфера для записи в файл
data_buffer = [] # инициализация буфера
buffer_count = 0 # счетчик записей в буфере

if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
	data_buffer.append(['date', 'lat', 'lon', 'alt', 'speed']) # запись заголовков, если выходной файл пуст

# Запуск фонового процесса обработки команды остановки приложения
threading.Thread(target=wait_for_exit, daemon=True).start()

options=Options()
options.add_argument('--headless')  # невидимый режим
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_argument('--window-size=1920,1200')
options.add_argument('--log-level=3')
options.add_argument('--silent')

driver = webdriver.Chrome(options=options)

# Скрыть WebDriver признаки
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Сбор данных о положении МКС с сайта НАСА
print("Подключение к сайту NASA")
driver.get("https://www.nasa.gov/spot-the-station/")

print("Поиск фрейма с телеметрией МКС")
iframe = driver.find_element(By.XPATH, "//iframe[@src='https://isstracker.spaceflight.esa.int/index.php']")
driver.switch_to.frame(iframe)

# Ожидание любого элемента с данными чтобы убедиться в загрузке
print("Ожидание загрузки данных")
wait = WebDriverWait(driver, 60)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id='isst_dt_data']")))

file = open(file_path, 'a', newline='', encoding='utf-8')
writer = csv.writer(file, delimiter=';')

try:
	print(f"Сбор данных\nДля выхода введите 'exit' и нажмите 'Enter'\n")
	print(f"{'дата':20} {'широта':10} {'долгота':10} {'высота':8} {'скорость':10}")	

	while not stop_flag:
		# Парсим данные
		timestamp = strftime("%Y-%m-%d %H:%M:%S")
		lat = driver.find_element(By.ID, "isst_lat").text
		lon = driver.find_element(By.ID, "isst_lon").text
		alt = driver.find_element(By.ID, "isst_alt").text
		spd = driver.find_element(By.ID, "isst_spd").text

		print(f"{timestamp:20} {lat:10} {lon:10} {alt:8} {spd:10}")
		data_buffer.append([timestamp, lat, lon, alt, spd])
		buffer_count += 1

		if buffer_count >= BUFFER_SIZE:					
			writer.writerows(data_buffer)
			file.flush()
			data_buffer = [] # сброс буфера
			buffer_count = 0 # сброс счетчика записей в буфере	
		
		# ожидание 45 сек до  записи
		for i in range(45):
			if stop_flag == True:
				break
			sleep(1)			
	
except Exception as e:
	print(f"error {e}")

finally:
	if data_buffer:
		writer.writerows(data_buffer) # запись данных из буфера в файл
		file.flush() 
		file.close()

	if driver:
		driver.switch_to.default_content()
		driver.quit()
		print("Браузер закрыт")