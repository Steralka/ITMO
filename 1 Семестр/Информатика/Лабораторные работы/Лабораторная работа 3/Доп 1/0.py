import re

def f(text):
    text = text.split('/')
    s = [5, 7, 5]
    r = [0, 0, 0]
    if len(text) == 3:
        for i in range(len(text)):
            r[i] = len(re.findall(r'[ауоыиэяюёе]', text[i], re.IGNORECASE))
        if r == s:
            st = 'Хайку!'
        else:
            st = 'Не хайку.'
    else:
        st = 'Не хайку. Должно быть 3 строки.'
    return st

# 1
print('=' * 5 + ' 1 ' + '=' * 5)
text1 = 'Вечер за окном./ Еще один день прожит./ Жизнь скоротечна...'
print(f'Ввод\n{text1}\nВывод\n{f(text1)}')

# 2
print('=' * 5 + ' 2 ' + '=' * 5)
text2 = 'Просто текст'
print(f'Ввод\n{text2}\nВывод\n{f(text2)}')

# 3
print('=' * 5 + ' 3 ' + '=' * 5)
text3 = 'Как вишня расцвела! / Она с коня согнала / И князя-гордеца.'
print(f'Ввод\n{text3}\nВывод\n{f(text3)}')