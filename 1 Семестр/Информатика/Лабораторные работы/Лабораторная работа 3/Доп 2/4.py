import re


def f(words, step, text):
    print(re.findall(r'{}\w{}{}\w{}{}'.format(words[0], step, words[1], step, words[2]), text))

print(f('КРА', 1, 'КоРмА'))