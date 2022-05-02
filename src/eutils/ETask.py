
# Base
import threading
import _thread
import time

# Data structure
from queue import Queue

from src.eutils.ELog import getLogger

class _ETask(threading.Thread):

    # life circle control
    _sleep = True
    _alive = True

    # actual task
    _task = None

    def __init__(self, task=None):
        threading.Thread.__init__(self)
        self._task = task

    def run(self):

        while self._alive:
            if self._sleep != True:
                self._task.start()
                self._sleep = True
            else:
                time.sleep(1) # wait task



class ETask():

    _inPort = None
    _outPort = None

    _maxWaitTime = 10

    def start(self):
        self._task()

    def _task(self):
        print("no implement _task method...")

    def enableInPort(self):
        self._inPort = Queue()

    def enableOutPort(self):
        self._outPort = Queue()

    def getFromInPort(self):
        if self._inPort:
            return self._inPort.get(timeout=self._maxWaitTime)
        return None

    def putToOutPort(self, msg):
        if self._outPort:
            self._outPort.put(msg)



class ETaskManager(threading.Thread):

    __mLock = threading.Lock()

    __mTaskList = []
    __mSleepQueue = Queue()

    _DataLinks = {"startTask ID": "endTask"}

    __mMaxTaskNums = 5

    __mELog = getLogger()


    def __init__(self):
        threading.Thread.__init__(self)
        self.__mELog = getLogger(type(self))

    def run(self):

        while True:
            
            time.sleep(1)

            for task in self.__mTaskList:

                outPort = self.getOutPort(task._task)
                
                while outPort and outPort.empty() != True:

                    nextTask = self._DataLinks[id(task._task)]

                    inPort = self.getInPort(nextTask)

                    if inPort:
                        data = outPort.get()
                        inPort.put(data)
                        self.__mELog.info("data link: %s --(%s)--> %s" % (id(data), id(task._task), id(nextTask)))
                    else:
                        break


                if task._sleep == True:
                    
                    self.__mLock.acquire()
                    self.__mTaskList.remove(task)
                    self.__mLock.release()

                    task._task.__class__ = ETask
                    task._task = None
                    self.__mSleepQueue.put(task)
                
    
    def addTasks(self, tasks=[]):

        if len(tasks) != 0:
            if len(tasks) == 1:
                self.addTask(tasks[0])
            else:

                taskPre = tasks[0]
                tasks.remove(taskPre)

                self.__mELog.info("task usecase: " + str(tasks))

                for task in tasks:
                    self.addTask(taskPre, task)
                    taskPre = task

    def addTask(self, tPre, tNext=None):

        self.__mELog.info("add datalink: %s -> %s" % (id(tPre), id(tNext)))
        
        _etaskPre = self.__getETask(tPre)
        _etaskNext = self.__getETask(tNext)

        self._DataLinks[id(tPre)] = tNext

        if id(tNext) not in self._DataLinks:
            self._DataLinks[id(tNext)] = None

        self.__mLock.acquire()

        if _etaskPre:
            self.__mTaskList.append(_etaskPre)
        if _etaskNext:
            self.__mTaskList.append(_etaskNext)

        self.__mLock.release()

    def getInPort(self, etask):
        if etask:
            return etask._inPort
        return None

    def getOutPort(self, etask):
        if etask:
            return etask._outPort
        return None


    def __getETask(self, task):

        if task is None:
            return None

        for et in self.__mTaskList:
            if et._task == task:
                return None

        if self.__mSleepQueue.empty() != True or len(self.__mTaskList) + 1 > self.__mMaxTaskNums:
            _etask = self.__mSleepQueue.get()
        else:
            _etask = _ETask()
            _etask.start()

        _etask._task = task

        self.__mELog.info("add task %s to etask %s " % (id(task), id(_etask)))

        _etask._sleep = False

        return _etask



if __name__ == "__main__":

    print("test...")