'''
Author: SPeak Shen
Date: 2022-02-25 21:32:14
LastEditTime: 2022-03-11 19:58:37
LastEditors: SPeak Shen
Description: a tiny task manager
FilePath: /EasyUtils/src/eutils/ETask.py
trying to hard.....
'''
# Base
import threading
import _thread
import time

# Data structure
from queue import Queue

# EUtils modules
from . import DEFAULT_LOGGER


class ETask(threading.Thread):

    _mTaskArgs = None
    _mTaskReturnInfo = None

    # Process order
    # function map table, type is 'def func(this)'
    __mTasks = {
        "preProcess" : None,
        "task" : None,
        "postProcess" : None 
    }

    _mGC = None
    
    # Task attribute
    _mTaskStatus = None

    _mSleepTime = None

    def run(self):
        
        for status, task in self.__mTasks.items():

            if task is not None:
                self._mTaskStatus = status
                task(self)

    def setTasks(tasks=[]):
        if len(tasks) == 3:
            self.__mTasks = tasks

    def setPreProcess(self, preProc):
        self.__mTasks["preProcess"] = preProc

    def setTask(self, task):
        self.__mTasks["task"] = task

    def setPostProcess(self, postProc):
        self.__mTasks["postProcess"] = postProc

    def setGC(self, gc):
        self._mGC = gc



class ETaskManager(threading.Thread):

    __taskRunList = []
    __taskReadyList = []
    __gcInterval = 1
    __gcCnt = 0
    
    __mRunListLimit = 5
    __mMaxTaskNums = 20

    __mReadyListMutex = threading.Lock()
    __mRunListMutex = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def addTask(self, task):
        if len(self.__taskRunList) + len(self.__taskReadyList) < self.__mMaxTaskNums:
            self.__addTaskToWaitList(task)

    def run(self):
        while True:
            time.sleep(self.__gcInterval)
            self.__scheduler()

            if len(self.__taskRunList) == 0:
                self.__gcInterval = 5
            else:
                self.__gcInterval = 1

            self.__tryGC()
            if len(self.__taskRunList) == 0:
                time.sleep(5)

    def __scheduler(self):

        while len(self.__taskRunList) < self.__mRunListLimit and len(self.__taskReadyList):
            task = self.__taskReadyList[0]
            self.__removeTaskFromWaitList(task)
            self.__addTaskToRunList(task)
            task.start()

    def __tryGC(self):

        gcInfo = "try task gc: " +\
            "gc interval is " + str(self.__gcInterval) +\
            "; gc cnt = " + str(self.__gcCnt)

        DEFAULT_LOGGER.info(gcInfo)

        for task in self.__taskRunList:

            if not task.isAlive():
                if None != task._mGC:
                    # start gc listen thread...
                    _thread.start_new_thread(task._mGC, (task, ))
                else:
                    print("task %d: gc function is null" % id(task))
                self.__removeTaskFromRunList(task)
                #print("task %d:  removed from taskList" % id(task))

        self.__gcCnt = self.__gcCnt + 1
        
    def config(self, maxTaskNums=None, runListLimit=None):
        
        if maxTaskNums is not None:
            self.__mMaxTaskNums = maxTaskNums
        
        if runListLimit is not None:
            self.__mRunListLimit = runListLimit
        

    """ mutex method """

    def __addTaskToRunList(self, task):
        self.__mRunListMutex.acquire()
        self.__taskRunList.append(task)
        self.__mRunListMutex.release()

    def __removeTaskFromRunList(self, task):
        self.__mRunListMutex.acquire()
        self.__taskRunList.remove(task)
        self.__mRunListMutex.release()

    def __addTaskToWaitList(self, task):
        self.__mReadyListMutex.acquire()
        self.__taskReadyList.append(task)
        self.__mReadyListMutex.release()

    def __removeTaskFromWaitList(self, task):
        self.__mReadyListMutex.acquire()
        self.__taskReadyList.remove(task)
        self.__mReadyListMutex.release()


# defualt task manager
# DEFUALT_TASK_MANAGER = ETaskManager()


if __name__ == "__main__":

    print("test...")