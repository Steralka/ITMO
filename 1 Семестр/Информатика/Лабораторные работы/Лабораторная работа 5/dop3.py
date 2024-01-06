import csv
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

file = r'' # Здесь ввести путь csv файла
with open(f'{file}') as r_file:  
    file_reader = csv.reader(r_file, delimiter=',')
    arr = [[], [], [], []]
    text = ['Открытие', 'Макс', 'Мин', 'Закрытие']
    dates = ['03/09/18', '01/10/18', '01/11/18', '03/12/18'] # Здесь прописать даты (формат ДД/ММ/ГГ)
    count = 0
    for row in file_reader:
        if row[2] == dates[0]:
            arr[0].append([int(row[4][:row[4].find('.')]), int(row[5][:row[5].find('.')]), int(row[6][:row[6].find('.')]), int(row[7][:row[7].find('.')])])
        elif row[2] == dates[1]:
            arr[1].append([int(row[4][:row[4].find('.')]), int(row[5][:row[5].find('.')]), int(row[6][:row[6].find('.')]), int(row[7][:row[7].find('.')])])
        elif row[2] == dates[2]:
            arr[2].append([int(row[4][:row[4].find('.')]), int(row[5][:row[5].find('.')]), int(row[6][:row[6].find('.')]), int(row[7][:row[7].find('.')])])
        elif row[2] == dates[3]:
            arr[3].append([int(row[4][:row[4].find('.')]), int(row[5][:row[5].find('.')]), int(row[6][:row[6].find('.')]), int(row[7][:row[7].find('.')])])

    plt.figure(figsize=(14, 7))
    for i in range(4):
        data = pd.DataFrame(arr[i], columns=text)
        plt.subplot(2, 2, i + 1)
        sns.boxplot(data=data)
        plt.title(f'Данные на {dates[i]}')
    plt.subplots_adjust(wspace=0.5, hspace=0.5)
    plt.show()