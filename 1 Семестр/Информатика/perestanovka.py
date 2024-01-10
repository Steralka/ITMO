import math
def f(z: int, n: int, t: int) -> str:
    res = z
    s = [i for i in range(1, n + 1)]
    l = dict()
    for j in range(math.factorial(n)):
        p = j
        r = [0] * len(s)
        a = ''.join(map(str, s))
        sc = ''
        c = 2
        while p > 0:
            sc += str(p % c)
            p //= c
            c += 1
        sc = list((sc[::-1].zfill(len(s) - 1)))
        for i in sc:
            ind = int(i) + 1
            while r[-ind:].count(0) - 1 != int(i):
                ind += 1
            r[-ind] = a[-1]
            a = a[:-1]
        r[r.index(0)] = a[-1]
        l[''.join(r)] = j
    if t == 1:
        return f'Номер перестановки: {res} - результат: {list(l.keys())[list(l.values()).index(z)]}'
    else:
        return f'Номер перестановки: {l[str(res)]} - результат: {res}'

print(f(12345, 5, 2)) 
#z - перестановку или номер перестановки
#n - число 
#t - 1 - поиск перестановки 2 - поиск номера перестановки

# КОД НЕ ОПТИМИЗИРОВАН ДЛЯ БОЛЬШИХ ФАКТОРИАЛАХ! СКОРО БУДЕТ ПЕРЕПИСАН.
