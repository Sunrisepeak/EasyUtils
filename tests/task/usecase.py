'''
Author: SPeak Shen
Date: 2022-02-25 21:34:48
LastEditTime: 2022-05-04 17:36:52
LastEditors: SPeak
Description: 
FilePath: /EasyUtils/tests/task/usecase.py
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

from src.test import WTask, RTask, RWTask


# set log level to observer run status
tm = ETaskManager()
tm.start()

# usecase
tasks = []
tasks.append(WTask())
for i in range(0, 8):
    tasks.append(RWTask())
tasks.append(RTask())

print(str(tasks))

tm.addTasks(tasks)


