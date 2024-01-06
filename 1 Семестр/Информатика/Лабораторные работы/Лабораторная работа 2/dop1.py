code = list(map(int, input()))
error = {0: 'нет',
1: 'r1',
2: 'r2',
3: 'i1',
4: 'r3',
5: 'i2',
6: 'i3',
7: 'i4'}
ic = [code[2], code[4], code[5], code[6]]
s1 = str(int(((code[0] != code[2]) != code[4]) != code[6]))
s2 = str(int(((code[1] != code[2]) != code[5]) != code[6])) 
s3 = str(int(((code[3] != code[4]) != code[5]) != code[6]))
sb = int((s1 + s2 + s3)[::-1], 2)
isn = [3, 5, 6, 7]
if sb in isn: ic[isn.index(sb)] = 1 - code[sb - 1]
ot = ''
for i in ic: ot += str(i)
print(f'Ошибка в {error[sb]}')
print(f'Правильное сообщение: {ot}') 