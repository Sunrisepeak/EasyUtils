'''
Author: SPeak Shen
Date: 2022-03-12 12:27:00
LastEditTime: 2022-04-25 20:39:24
LastEditors: SPeak Shen
Description: 
FilePath: /EasyUtils/test/elist.py
trying to hard.....
'''
import sys
import os

sys.path.append(
    os.getcwd()
)

from src.eutils import EList
from src.eutils import LNode


################ test LNode (compare address info) ################
ln1 = LNode(5)
ln2 = LNode(6, next=ln1)
ln3 = ln2.next
ln4 = ln1
ln5 = LNode(5)

ls = []
ls.append(ln1)
ls.append(ln2)
ls.append(ln3)
ls.append(ln4)
ls.append(ln5)

print(ln1, "data = " + str(ln1.data))
print(ln2, "data = " + str(ln2.data))
print(ln3, "data = " + str(ln3.data))
print(ln4, "data = " + str(ln4.data))
print(ln5, "data = " + str(ln5.data))

print("change ln3 and ln4, ln5 node data by assign")
ln3.data = 7
ln4.data = 8
ln5.data = 8

print(ln1, "data = " + str(ln1.data))
print(ln2, "data = " + str(ln2.data))
print(ln3, "data = " + str(ln3.data))
print(ln4, "data = " + str(ln4.data))
print(ln5, "data = " + str(ln5.data))

def change(lnode, data):
    lnode.data = data
print("change ln3 and ln4, ln5 node data by func")
change(ln3, 9)
change(ln4, 10)
change(ln5, 10)


print(ln1, "data = " + str(ln1.data))
print(ln2, "data = " + str(ln2.data))
print(ln3, "data = " + str(ln3.data))
print(ln4, "data = " + str(ln4.data))
print(ln5, "data = " + str(ln5.data))


################ test EList ################
el = EList()

for i in range(0, 10):
    el.add(i)

for val in el:
    print(val, " ", end="")

el.delete(8)
el.push(ln5)
print()

for val in el:
    print(val, " ", end="")

el.delete(ln5)
print()

for val in el:
    print(val, " ", end="")

print()

for l in ls:
    print(l.data, " ", end="")