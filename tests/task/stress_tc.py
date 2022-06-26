'''
Author: SPeak
Date: 2022-05-03 19:54:47
LastEditors: SPeak
LastEditTime: 2022-05-04 17:58:30
FilePath: /EasyUtils/tests/task/stress_tc.py
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
tm = ETaskManager(maxTaskNums=100, enableLog=False, logLevel=3)
tm.start()

rt = RTask()

# test 300 task
for i in range(0, 300):
    wt = WTask()
    tm.addTask(wt, rt)

while tm.taskNums() > 1 and tm.runTaskNums() > 1:
    print("TaskManager current task nums is %d" % tm.taskNums())
    print("TaskManager current ETask thread nums is %d" % tm._runTaskNums())
    print("TaskManager current Running of ETask thread nums is %d" % tm.runTaskNums())
    time.sleep(1)

print("test over, you can check log file info")