import re # импортируем библиотеку с регулярными выражениями

smile = ';<O' # смайл варианта
res = ['0', '48yufhtfhfhfhf;<Ohkjgjgjgjgj;<O jkhkjgjgjgjgjgjg', ';<O;<O;<O;<O;<O;<O;<O', 'hikgjgjfh', '5555'] # тестовые значения
for j in res: 
    r = re.findall(rf'{smile}', j)
    if r:
        print(f'Смайл {smile} в строке {j} встречается {len(r)} раз(а).')
    else:
        print(f'Смайл {smile} в строке {j} встречается 0 раз.')
