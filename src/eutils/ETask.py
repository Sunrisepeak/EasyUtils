
# Base
import threading
import time

# Data structure
from queue import Queue

from src.eutils.ELog import getLogger, DEFAULT_LOGGER

# user should not to use it directly, but to implement ETask
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
                self._task._ETask__start()
                self._sleep = True
            else:
                time.sleep(1) # wait task



class ETask():

    __mInPort = None
    __mOutPort = None

    __mMaxWaitTime = 10

    def etask(self):
        print("method not implement...")

    def start(self):
        self.etask()

    def _enableInPort(self):
        self.__mInPort = Queue()

    def _enableOutPort(self):
        self.__mOutPort = Queue()

    def _receiveMsg(self):
        if self.__mInPort:
            return self.__mInPort.get(timeout=self.__mMaxWaitTime)
        return None

    def _sendMsg(self, msg):
        if self.__mOutPort:
            self.__mOutPort.put(msg)

    def __start(self):
        self.etask()



class ETaskManager(threading.Thread):

    __mLock = threading.Lock()

    # need lock
    __mTaskRunList = []

    # only ETM thread using -- {"startTask ID": "endTask List"}
    __mDataLinks = {"startTask ID": "endTask List"}


    # thread safe
    __mTaskSleepQueue = Queue()
    __mTaskReadyQueue = Queue()


    # final var
    __mMaxTaskNums = 5
    __mELog = DEFAULT_LOGGER


    def __init__(self, maxTaskNums=5, lLevel=1):
        threading.Thread.__init__(self)

        self.__mMaxTaskNums = maxTaskNums
        self.__mELog = getLogger("EUTILS::ETaskManager")
        self.__mELog.config(logLevel=lLevel)

    def run(self):

        while True:
            
            self.__mELog.debug("run task list: "  + str(self.__mTaskRunList))

            # 1. check/modify task status and transport msg 
            for task in self.__mTaskRunList:

                self.__msgTransport(task)

                if task._sleep == True:
                    self.__mTaskRunList.remove(task)
                    self.__mTaskSleepQueue.put(task)

            # 2. process message cache
            self.__processMsgsCache()

            # 3. try run new task
            if self.__mTaskReadyQueue.empty():
                time.sleep(1)
            else:
                self.__trypStartNewETask()

    def taskNums(self):
        return self._runTaskNums + self.__mTaskReadyQueue.qsize()

    def runTaskNums(self):
        return len(self.__mTaskRunList)

    def _runTaskNums(self):
        return self.runTaskNums() + self.__mTaskSleepQueue.qsize()
                
    def addTasks(self, tasks=[]):

        if len(tasks) != 0:
            if len(tasks) == 1:
                self.addTask(tasks[0])
            else:
                taskPre = tasks[0]
                tasks.remove(taskPre)

                self.__mELog.debug("task usecase: " + str(tasks))

                for task in tasks:
                    self.addTask(taskPre, task)
                    taskPre = task

    def addTask(self, tPre, tNext=None):
        if tPre is None and tNext is None:
            self.__mELog.error("type is <None, None>, add task: <%s, %s> failed" % (str(tPre), str(tNext)))
            return
        elif tPre is None:
            tPre, tNext = tNext, tPre
        self.__mTaskReadyQueue.put([tPre, tNext])
        self.__mELog.debug("add task: <%s, %s>" % (str(tPre), str(tNext)))


    def __getInPort(self, etask):
        if etask:
            return etask._ETask__mInPort
        return None

    def __getOutPort(self, etask):
        if etask:
            return etask._ETask__mOutPort
        return None

    def __trypStartNewETask(self):
        while not self.__mTaskReadyQueue.empty():

            try:
                taskPair = self.__mTaskReadyQueue.get(timeout=1)
            except Exception as e:
                self.__mELog.warn(str(e))
                break
            
            self.__mELog.debug("try start new task: %s" % (str(taskPair)))

            if self.runTaskNums() + 2 <= self.__mMaxTaskNums:
                self.__addTaskAndStart(taskPair[0], taskPair[1])

            elif self.runTaskNums() + 1 <= self.__mMaxTaskNums and (id(taskPair[0]) in self.__mDataLinks or taskPair[1] is None):
                self.__addTaskAndStart(taskPair[0], taskPair[1])

            else:
                self.__mTaskReadyQueue.put(taskPair)
                break


    def __addTaskAndStart(self, tPre, tNext=None):

        self.__mELog.debug("start task: <%s, %s>" % (str(tPre), str(tNext)))
        
        _etaskPre, PBool = self.__allocAndBindETask(tPre)
        _etaskNext, NBool = self.__allocAndBindETask(tNext)

        if _etaskNext and _etaskPre:
            self.__createDataLink(_etaskPre._task, _etaskNext._task)
        elif _etaskPre:
            self.__createDataLink(_etaskPre._task)
        else:
            self.__mELog.warn("task already exist: <%s, %s>" % (str(tPre), str(tNext)))

        if PBool:
            self.__mTaskRunList.append(_etaskPre)
        if NBool:
            self.__mTaskRunList.append(_etaskNext)

    def __msgTransport(self, task):

        self.__mELog.debug("[%s]: transport msg" % str(task._task))

        outPort = self.__getOutPort(task._task)

        tList = self.__mDataLinks[id(task._task)]

        if len(tList) == 0:
            return


        while outPort and not outPort.empty():

            for nextTask in tList:

                inPort = self.__getInPort(nextTask)

                if inPort:
                    data = outPort.get()
                    inPort.put(data)
                    self.__mELog.debug("data flow: %s --(%s)--> %s" % (id(data), id(task._task), id(nextTask)))


    def __allocAndBindETask(self, task):

        if task is None:
            return None, False

        for et in self.__mTaskRunList:
            if et._task == task:
                return et, False

        if not self.__mTaskSleepQueue.empty() or len(self.__mTaskRunList) + 1 > self.__mMaxTaskNums:
            _etask = self.__mTaskSleepQueue.get()
            self.__processMsgCache(_etask)
        else:
            _etask = _ETask()
            _etask.start()

        _etask._task = task

        self.__mELog.debug("Bind task %s to etask %s " % (id(task), id(_etask)))

        _etask._sleep = False

        return _etask, True

    def __createDataLink(self, src, dst=None):

        dstID = id(dst)

        if id(src) in self.__mDataLinks:
            self.__mDataLinks[id(src)].append(dst)
        else:
            if dst:
                self.__mDataLinks[id(src)] = [ dst ]
            else:
                self.__mDataLinks[id(src)] = [ ]
                dstID = '0'
        
        if id(dst) not in self.__mDataLinks:
            self.__mDataLinks[id(dst)] = [ ]

        self.__mELog.debug("create data link: [%s --> %s]" % (id(src), dstID))


    def __processMsgCache(self, task):

        self.__msgTransport(task)
        del self.__mDataLinks[id(task._task)]

    def __processMsgsCache(self):

        # Note: actual cache process nums is less then or equal the var 'cacheProcessNums'
        # because ready task is great than or equal 'self.__mTaskReadyQueue.qsize()'
        # Ready task would be dealing with cache of alloc _ETask from sleep queue  
        cacheProcessNums = self.__mTaskSleepQueue.qsize() - self.__mTaskReadyQueue.qsize()

        while cacheProcessNums > 0:

            task = self.__mTaskSleepQueue.get()
            self.__processMsgCache(task)

            cacheProcessNums -= 1
            


if __name__ == "__main__":

    print("Hello ETask")