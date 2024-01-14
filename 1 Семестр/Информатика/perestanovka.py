import math

def f(z: int, n: int, t: int) -> str:
    s = [i for i in range(1, n + 1)]
    if t == 1:
        p = z
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
        return f'Для номера перестановки: {z} будет перестановка: {"".join(r)}'
    if t == 2:
        sc = []
        sp = list(map(int, str(z)))
        for i in range(n, 1, -1):
            sc.append(len(sp) - sp.index(i) - 1)
            sp.remove(i)
        return f'Для перестановки: {z} будет номер перестановки: {sum(sc[-i] * math.factorial(i) for i in range(len(sc), 0, -1))}'

print(f(93, 5, 1)) # найдем перестановку
print(f(43215, 5, 2)) # найдем номер перестановки
#z - перестановку или номер перестановки
#n - число
#t - 1 - поиск перестановки 2 - поиск номера перестановки
