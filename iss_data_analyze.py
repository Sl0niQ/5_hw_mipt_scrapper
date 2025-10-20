import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

FILE_PATH = 'iss_data.csv' # имя файла с сырыми данными
CSV_SEPARATOR = ';'        # разделитель в csv файле с данными
SPEED_SUFFIX_LENGTH = 5    # для отсечения 5ти символов ' km/h'

if os.path.isfile(FILE_PATH):

	# чтение csv файла
	df = pd.read_csv(FILE_PATH, usecols=['date', 'speed'], sep=CSV_SEPARATOR)

	# обработка данных, преобразование типов
	df['speed'] = df['speed'].str[:-SPEED_SUFFIX_LENGTH].astype(float)
	df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

	# анализ данных
	max_speed = df['speed'].max()
	min_speed = df['speed'].min()

	# построение графика
	plt.figure(figsize=(12, 6))
	plt.plot(df['date'], df['speed'], linewidth=2)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))   # только часы:минуты
	plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30)) # шаг 30 минут
	
	# Заголовки, название осей
	plt.title(f"Изменение скорости МКС: max={max_speed} км.ч/min={min_speed} км/ч", fontsize=14, fontweight='bold')
	plt.xlabel("Время", fontsize=12)
	plt.ylabel("Скорость, км/ч", fontsize=12)
	plt.grid(True, alpha=0.3)

	# вывод на экран
	plt.show()

else:
	print(f"файл {file_path} не найден")