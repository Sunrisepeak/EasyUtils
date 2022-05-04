'''
Author: SPeak Shen
Date: 2022-02-25 21:34:48
LastEditTime: 2022-05-03 17:53:39
LastEditors: SPeak
Description: 
FilePath: /EasyUtils/test/task/multi_to_one.py
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

from src.test import WTask, RTask


# set log level to observer run status
tm = ETaskManager(logLevel=0)
tm.start()

rt = RTask()

tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)
tm.addTask(WTask(), rt)