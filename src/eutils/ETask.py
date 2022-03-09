'''
Author: SPeak Shen
Date: 2022-02-25 21:32:14
LastEditTime: 2022-03-08 19:33:48
LastEditors: SPeak Shen
Description: a tiny task manager
FilePath: /EasyUtils/src/eutils/ETask.py
trying to hard.....
'''
import threading
import _thread
import time

from . import DEFAULT_LOGGER


class ETask(threading.Thread):

    task = None
    taskArgs = None
    taskReturnInfo = None
    gc = None
    sleepTime = None

    def run(self):
        #print("start task:  ", id(self))
        if self.taskArgs == None:
            self.taskReturnInfo = self.task()
        else:
            self.taskReturnInfo = self.task(self.taskArgs)
        #print("end task:   ", id(self))

    def setTask(self, task, args=None):
        #print("...")
        self.task = task
        if args != None:
            self.taskArgs = args

    def setGC(self, gc, sleepTime=1):
        self.gc = gc
        self.sleepTime = sleepTime


class ETaskManager(threading.Thread):

    __taskRunList = []
    __taskWaitList = []
    __gcInterval = 1
    __gcCnt = 0
    
    __mRunListLimit = 5
    __mMaxTaskNums = 20

    waitListMutex = threading.Lock()
    runListMutex = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def addTask(self, task):
        if len(self.__taskRunList) + len(self.__taskWaitList) < self.__mMaxTaskNums:
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

        while len(self.__taskRunList) < self.__mRunListLimit and len(self.__taskWaitList):
            task = self.__taskWaitList[0]
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
                if None != task.gc:
                    # start gc listen thread...
                    _thread.start_new_thread(task.gc, (task, ))
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
        self.runListMutex.acquire()
        self.__taskRunList.append(task)
        self.runListMutex.release()

    def __removeTaskFromRunList(self, task):
        self.runListMutex.acquire()
        self.__taskRunList.remove(task)
        self.runListMutex.release()

    def __addTaskToWaitList(self, task):
        self.waitListMutex.acquire()
        self.__taskWaitList.append(task)
        self.waitListMutex.release()

    def __removeTaskFromWaitList(self, task):
        self.waitListMutex.acquire()
        self.__taskWaitList.remove(task)
        self.waitListMutex.release()


# defualt task manager
# DEFUALT_TASK_MANAGER = ETaskManager()


if __name__ == "__main__":

    print("test...")