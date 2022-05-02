'''
Author: SPeak Shen
Date: 2022-02-25 21:34:48
LastEditTime: 2022-05-02 23:19:21
LastEditors: SPeak
Description: 
FilePath: /EasyUtils/test/task.py
trying to hard.....
'''

import sys
import os
import time

sys.path.append(
    os.getcwd()
)

from src.eutils import ETask
from src.eutils import ETaskManager

class WTask(ETask):

    def __init__(self):
        self.enableOutPort()

    def _task(self):
        i = 0
        while i < 5:
            self.putToOutPort("hello task " + str(i))
            i = i + 1
        print("WTask over")

class RTask(ETask):

    def __init__(self):
        self.enableInPort()

    def _task(self):
        while True:
            time.sleep(1)
            try:
                msg = self.getFromInPort()
            except:
                break
            print(msg)

class RWTask(ETask):

    def __init__(self):
        self.enableInPort()
        self.enableOutPort()

    def _task(self):
        time.sleep(1)
        while True:
            try:
                msg = self.getFromInPort()
            except Exception as e:
                print(str(e))
                break
            print(str(type(self)) + " " + msg + "(%s)" % id(self))
            self.putToOutPort(msg)

tm = ETaskManager()
tm.start()

"""
rt = RTask()

wt = WTask()

wt.start()
wt.__class__ = ETask
wt.start()

# one by one
tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)

# multi by one
time.sleep(5)
tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)

time.sleep(5)
"""
# usecase
wt = WTask()

rwts = [RWTask() for i in range(0, 10)]

rt = RTask()

tasks = []
tasks.append(wt)

for rwt in rwts:
    tasks.append(rwt)

tasks.append(rt)

print(tasks)

tm.addTasks(tasks)


