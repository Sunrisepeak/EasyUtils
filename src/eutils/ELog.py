'''
Author: SPeak Shen
Date: 2022-02-25 21:32:14
LastEditTime: 2022-02-28 21:12:56
LastEditors: SPeak Shen
Description: a base log system...
FilePath: /EasyUtils/src/eutils/ELog.py
trying to hard.....
'''
import _thread
import os
import time
from queue import Queue
import threading
import sys


class LogBase(object):
    _mOutputFile = None
    _mOutputConsole = None

    """ error < warning < debug < info"""
    _mLogLevelMap = None
    _mLogLevel = None

    def __init__(self):

        self._mLogLevelMap = {"error": 0, "warn": 1, "debug": 2, "info": 3}
        self._mLogLevel = self._mLogLevelMap["error"]

        self.config(console=True)

    def info(self, message):

        if self._mLogLevel <= self._mLogLevelMap["info"]:
            message = "[info]: " + message

            self._print(message)

    def debug(self, message):

        if self._mLogLevel <= self._mLogLevelMap["debug"]:
            message = "[debug]: " + message

            self._print(message)

    def warn(self, message):

        if self._mLogLevel <= self._mLogLevelMap["warn"]:
            message = "[warn]: " + message

            self._print(message)

    def error(self, message):

        if self._mLogLevel <= self._mLogLevelMap["error"]:
            message = "[error]: " + message

            self._print(message)

    def _print(self, message):

        print("method no implement...")

    def _formatLogMessage(self, message):
        timeInfo = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        parentPocessID = os.getppid()
        processID = os.getpid()
        threadID = threading.current_thread().ident

        return f"%s %d %d %d {message} " % (timeInfo, parentPocessID, processID, threadID)

    def config(self, console=None, logFile=None, logLevel=None):

        if console != None:
            self._mOutputConsole = console

        if logFile != None:
            self.__configLogFile(logFile)

        if logLevel != None:
            self.__configLogLevel(logLevel)

    def __configLogFile(self, logFile):

        print(logFile)

        try:
            self._mOutputFile = open(logFile, 'a+')

            print("open file %s success" % logFile)

        except Exception:

            print("open file %s filed..." % logFile)


    def __configLogLevel(self, logLevel):

        print(logLevel)


class ELog(LogBase, threading.Thread):

    __mInputQueue = None
    __mOutputQueue = None

    qLock = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        LogBase.__init__(self)

        self.__mInputQueue = Queue()
        self.__mOutputQueue = Queue()

    def run(self):
        i = 0
        while True:
            time.sleep(2)
            # print(" try print: " + str(i))
            self.tryFlush()
            i = i + 1

    def _print(self, message):

        message = self._formatLogMessage(message)
        self.__put2MQ(message)

    def tryFlush(self):

        while not self.__mOutputQueue.empty():

            logInfo = self.__mOutputQueue.get()

            if self._mOutputConsole:
                print(logInfo)

            if self._mOutputFile is not None:
                print("debug log file print....")

                try:

                    self._mOutputFile.write(logInfo + "\n")

                except Exception:

                    print("log output file filed....")

        if self._mOutputFile is not None:
            self._mOutputFile.flush()

        self.__exchangeMQ()

    def __put2MQ(self, message):
        # todo thead lock? Queue is a data struct of thread safe
        # print("input <-- " + message)
        self.__mInputQueue.put(message)

    def __exchangeMQ(self):
        # self.qLock.acquire()
        print(self.__mInputQueue, self.__mOutputQueue)
        self.__mInputQueue, self.__mOutputQueue = self.__mOutputQueue, self.__mInputQueue
        print(self.__mInputQueue, self.__mOutputQueue)
        # self.qLock.release()


def getLogger():

    log = ELog()

    timeInfo = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    defaultLogFile = os.getcwd() + "/" + timeInfo + "_" + "eutils.elog"

    log.config(logFile=defaultLogFile)
    log.config(console=False)

    log.info("default log system init done.")

    log.start()

    return log


DEFAULT_LOGGER = getLogger()

""" ----------------------------------------- Test Code ----------------------------------------- """

"""

sys._getframe().f_code.co_filename  #当前文件名
sys._getframe(0).f_code.co_name     #当前函数名
sys._getframe().f_lineno            #当前行号

"""

"""
def printLog(level, logger=None):

    if logger is None:
        logger = DEFAULT_LOGGER

    info = "%s %s" % (sys._getframe().f_code.co_filename, sys._getframe(0).f_code.co_name)

    print(info)

    for i in range(0, 10):

        message = info + "hello world " + str(i)

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

    myLogger = getLogger()

    lFile= os.getcwd() + "/eu_test.log"

    print(lFile)

    myLogger.config(logFile=lFile)

    myLogger.info("test")

    _thread.start_new_thread(printLog, (0, myLogger))
    _thread.start_new_thread(printLog, (1, myLogger))
    _thread.start_new_thread(printLog, (2, myLogger))
    _thread.start_new_thread(printLog, (3, myLogger))

    time.sleep(10)
"""