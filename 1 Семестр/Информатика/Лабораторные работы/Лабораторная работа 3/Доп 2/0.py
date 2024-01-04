import re

def f(text):
    k = re.findall(r'^[a-zA-Z0-9._]+\@([a-zA-Z.]+\.[a-zA-Z]+)$', text)
    if len(k) == 1:
        return k[0]
    return 'Fail!'

#1
print('=' * 5 + ' 1 ' + '=' * 5)
text1 = 'students.spam@yandex.ru'
print(f(text1))

#2
print('=' * 5 + ' 2 ' + '=' * 5)
text2 = 'example@example'
print(f(text2))

#3
print('=' * 5 + ' 3 ' + '=' * 5)
text3 = 'example@example.com'
print(f(text3))