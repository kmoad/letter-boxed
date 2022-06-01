from letter_boxed import PrefixNode
import traceback

t = PrefixNode(['HAY','HELLO','GOODBYE'])
print(len(t))
print(t['H'].prefix)
print('H' in t)
print('G' in t)
try:
    print(t['G'])
except KeyError as e:
    print('not there')
print(t.get('G','not there'))
for node in t:
    print(node.prefix)
try:
    print(t['HAYWARD'])
except:
    traceback.print_exc()