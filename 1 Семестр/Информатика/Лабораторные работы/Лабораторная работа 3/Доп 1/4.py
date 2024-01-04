import re

def f(text):
    r = re.sub(r'\d\d:\d\d:\d\d', '(TBD)', text)
    r = re.sub(r'\d\d:\d\d', '(TBD)', r)
    return r

text = 'Уважаемые студенты! В эту субботу в 15:00 планируется доп. занятие на 2 часа. То есть в 17:00:01 оно уже точно кончится.'
print(f(text))


# Переделать 