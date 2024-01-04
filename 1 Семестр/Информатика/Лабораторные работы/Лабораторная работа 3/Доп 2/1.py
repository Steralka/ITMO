import re

text = 'Классное слово – обороноспособность, которое должно идти после слов: трава и молоко'
sp = []
arr = re.findall(r'\w+', text)
for elem in arr:
    for letter in 'аоуыэяёюие':
        pattern = re.compile(rf'{letter}', re.IGNORECASE)
        new_word = re.sub(pattern, '', elem)
        pattern2 = re.compile(r'[аоуыэяёюие]', re.IGNORECASE)
        if not re.search(pattern2, new_word):
            sp.append(elem)
k = sorted(sp, key=len)
for i in k: print(i)