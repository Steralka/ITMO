from functools import reduce


a = input("Введите 16 двоичных символов (первое число), можно с точками: ").strip()
b = input("Введите 16 двоичных символов (второе число), можно с точками: ").strip()
a = a.replace('.', '')
b = b.replace('.', '')
if a.count('0') + a.count('1') == 16 and b.count('0') + b.count('1') == 16:
    arr_transfer = [0] * 17
    res = ''
    for i in range(16):
        res = str((int(a[-i - 1]) + int(b[-i - 1]) + arr_transfer[i]) % 2) + res
        arr_transfer[i + 1] = (int(a[-i - 1]) + int(b[-i - 1]) + arr_transfer[i]) // 2


    if res[0] == '1':
        for i in range(1, 16):
            if '1' in res[i+1:]:
                res[i] == str(not(bool(res[i])))


    flags = {}
    flags['cf'] = arr_transfer[16]
    flags['zf'] = 1 - reduce(lambda a, b: int(a) or int(b), arr_transfer)
    flags['of'] = (arr_transfer[15] + arr_transfer[16]) % 2
    flags['sf'] = int(res[0])
    flags['af'] = int(arr_transfer[4])
    flags['pf'] = 1 - res[8:].count('1') % 2
    print(res)
    print('Выставлены флаги: ', end='')
    for item in flags:
        if flags[item] == 1:
            print(item + ' ', end='')
else:
    print('Вы ввели какую то хуйню! Попробуйте снова.')
