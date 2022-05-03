
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
                
                try:
                    if self._task is not None:
                        self._task._ETask__start()
                except Exception as e:
                    DEFAULT_LOGGER.error(" task %s runtime error" % str(self._task))

                self._sleep = True

            else:
                time.sleep(1) # wait task



class ETask():

    __mInPort = None
    __mOutPort = None

    __mMaxWaitTime = 0x4554 # ET

    def etask(self):
        print("method not implement...")

    def start(self):
        self.etask()

    def _enableInPort(self):
        self.__mInPort = Queue()

    def _enableOutPort(self):
        self.__mOutPort = Queue()

    def _setMaxWaitTime(self, maxWaitTime):
        self.__mMaxWaitTime = maxWaitTime

    def _receiveMsg(self, maxWaitTime=None):

        if maxWaitTime is None:
            maxWaitTime = self.__mMaxWaitTime

        if self.__mInPort:
            try:
                msg = self.__mInPort.get(timeout=maxWaitTime)
            except Exception as e:
                DEFAULT_LOGGER.warn("%s receive msg timeout." % str(self))
                raise
            return msg
        return None

    def _sendMsg(self, msg, maxWaitTime=None):

        if maxWaitTime is None:
            maxWaitTime = self.__mMaxWaitTime

        if self.__mOutPort:
            self.__mOutPort.put(msg,timeout=maxWaitTime)

    def __start(self):
        self.etask()



class ETaskManager(threading.Thread):

    __mLock = threading.Lock()

    # only ETM thread using -- {"startTask ID": "endTask List"}
    __mTaskRunList = []
    __mDataLinks = {"startTask ID": "endTask List"}


    # thread safe
    __mTaskSleepPool = Queue()
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

            sleepTask = []

            # 1. check/modify task status and transport msg 
            for task in self.__mTaskRunList:

                self.__msgTransport(task)

                if task._sleep == True:
                    sleepTask.append(task)

            # 2. move sleep task to sleep queue
            for task in sleepTask:
                self.__mTaskRunList.remove(task)
                self.__mTaskSleepPool.put(task)


            # 3. process message cache
            self.__processMsgsCache()

            # 4. try run new task
            if self.__mTaskReadyQueue.empty():
                time.sleep(1)
            else:
                self.__trypStartNewETask()

            # 5. thread/task collection
            self.__TC()

    def taskNums(self):
        return self._runTaskNums() + self.__mTaskReadyQueue.qsize()

    def runTaskNums(self):
        return len(self.__mTaskRunList)

    def _runTaskNums(self):
        return self.runTaskNums() + self.__mTaskSleepPool.qsize()
                
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
            
            existInPort = False

            for nextTask in tList:
                
                inPort = self.__getInPort(nextTask)

                if inPort:
                    existInPort = True
                    data = outPort.get()
                    inPort.put(data)
                    self.__mELog.debug("data flow: %s --(%s)--> %s" % (id(data), id(task._task), id(nextTask)))
                else:
                    self.__mELog.warn("src %s --> dst %s, not found inport in dst" % (str(task._task), str(nextTask)))

            if not existInPort:
                self.__mELog.warn("[Bug?] src %s --> dst %s, not found inport in dst task list" % (str(task._task), str(tList)))
                break


    def __allocAndBindETask(self, task):

        if task is None:
            return None, False

        for et in self.__mTaskRunList:
            if et._task == task:
                return et, False

        if not self.__mTaskSleepPool.empty() or len(self.__mTaskRunList) + 1 > self.__mMaxTaskNums:
            _etask = self.__mTaskSleepPool.get()
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

        if task._task:
            self.__msgTransport(task)
            
        if id(task._task) in self.__mDataLinks:
            del self.__mDataLinks[id(task._task)]

        task._task = None

    def __processMsgsCache(self):

        # Note: actual cache process nums is less then or equal the var 'cacheProcessNums'
        # because ready task is great than or equal 'self.__mTaskReadyQueue.qsize()'
        # Ready task would be dealing with cache of alloc _ETask from sleep queue  
        cacheProcessNums = self.__mTaskSleepPool.qsize() - self.__mTaskReadyQueue.qsize()

        while cacheProcessNums > 0:

            task = self.__mTaskSleepPool.get()
            self.__processMsgCache(task)

            # Part ETask (~ 1/4)
            if cacheProcessNums % 4:
                self.__mTaskSleepPool.put(task)

            cacheProcessNums -= 1

    def __TC(self):

        while self.runTaskNums() / 2 + 1 < self.__mTaskSleepPool.qsize():

            self.__mTaskSleepPool.get()

            


if __name__ == "__main__":

    print("Hello ETask")