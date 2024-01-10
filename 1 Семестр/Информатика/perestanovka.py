import math
def f(z, n, t):
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
        return f'Номер перестановки: {l[res]} - результат: {res}'
    else:
        return f'Номер перестановки: {res} - результат: {list(l.keys())[list(l.values()).index(z)]}'

print(f(93, 5, 2))
