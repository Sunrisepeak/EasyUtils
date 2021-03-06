'''
Author: SPeak Shen
Date: 2022-02-28 20:59:08
LastEditTime: 2022-05-04 15:29:56
LastEditors: SPeak
Description: 
FilePath: /EasyUtils/tests/elog/func_test.py
trying to hard.....
'''

import sys
import os
import _thread
import time

sys.path.append(
    os.getcwd()
)

from src.eutils import ELog
from src.eutils import getLogger

gLogger = getLogger("ELog Test")

def printLog(level, logger=None):

    if logger is None:
        logger = gLogger

    info = "%s %s" % (sys._getframe().f_code.co_filename, sys._getframe(0).f_code.co_name)

    print(info)

    for i in range(0, 10):

        message = info + " hello world " + str(i)

        if level == 0:
            logger.info(message)
        elif level == 1:
            logger.debug(message)
        elif level == 2:
            logger.warn(message)
        else:
            logger.error(message)

        time.sleep(1)


if __name__ == "__main__":

    myLogger = getLogger("my logger")

    lFile= os.getcwd() + "/eu_test.log"

    print(lFile)

    myLogger.config(logFile=lFile)

    myLogger.info("test")

    _thread.start_new_thread(printLog, (0, myLogger))
    _thread.start_new_thread(printLog, (1, myLogger))
    _thread.start_new_thread(printLog, (2, gLogger))
    _thread.start_new_thread(printLog, (3, myLogger))

    time.sleep(10)