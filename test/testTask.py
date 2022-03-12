'''
Author: SPeak Shen
Date: 2022-02-25 21:34:48
LastEditTime: 2022-03-11 19:45:29
LastEditors: SPeak Shen
Description: 
FilePath: /EasyUtils/test/testTask.py
trying to hard.....
'''

import sys
import os
import time

sys.path.append(
    os.getcwd()
)

from src.eutils import ETask as Task
from src.eutils import ETaskManager as TaskManager

# start task manager
TASK_MANAGER = TaskManager()


def myTask1():
    for i in range(0, 10):
        print("hello task1: ", str(i))
        time.sleep(1)


def myTask2(arg):
    for i in range(0, 5):
        print("hello task2: ", str(i), arg)
        time.sleep(2)

def myPreProcess():
    pass

def myTask2GC(task):
    print("gc over... %s " % str(task._mSleepTime))

def myPostProcess():
    pass

t1, t2 = Task(), Task()

t1.setTask(myTask1)
t2.setTask(myTask2)

t2.setGC(myTask2GC)

TASK_MANAGER.addTask(t1)
TASK_MANAGER.addTask(t2)