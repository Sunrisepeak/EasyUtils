'''
Author: SPeak
Date: 2022-05-03 19:54:47
LastEditors: SPeak
LastEditTime: 2022-05-03 23:17:22
FilePath: /EasyUtils/test/task/stress_tc.py
Description: 

'''

import sys
import os
import time

sys.path.append(
    os.getcwd()
)

from src.eutils import ETask
from src.eutils import ETaskManager

from src.test import WTask, RTask

# set log level to observer run status
tm = ETaskManager(lLevel=0, maxTaskNums=100)
tm.start()

rt = RTask()

# test 300 task
for i in range(0, 150):
    wt = WTask()
    tm.addTask(wt, rt)
    tm.addTask(WTask(), wt) # this is error task pair

while tm.taskNums() > 1:
    print("TaskManager current task nums is %d" % tm.taskNums())
    print("TaskManager current ETask thread nums is %d" % tm._runTaskNums())
    print("TaskManager current Running of ETask thread nums is %d" % tm.runTaskNums())
    time.sleep(1)

print("test over")