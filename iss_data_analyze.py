import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

file_path = 'iss_data.csv'

if os.path.isfile(file_path):

	# чтение csv файла
	df = pd.read_csv('iss_data.csv', usecols=['date', 'speed'], sep=';')

	# обработка данных, преобразование типов
	df['speed'] = df['speed'].str[:-4].astype(float)
	df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

	# построение графика
	plt.figure(figsize=(12, 6))
	plt.plot(df['date'], df['speed'], linewidth=2)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))   # только часы:минуты
	plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30)) # шаг 30 минут
	#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
	#plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
	#plt.xticks(rotation=0)

	# Заголовки, название осей
	plt.title("Изменение скорости МКС", fontsize=14, fontweight='bold')
	plt.xlabel("Время", fontsize=12)
	plt.ylabel("Скорость, км/ч", fontsize=12)
	plt.grid(True, alpha=0.3)

	# вывод на экран
	plt.show()

else:
	print(f"файл {file_path} не найден")