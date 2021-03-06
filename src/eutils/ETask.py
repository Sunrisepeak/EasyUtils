
# Base
import re
import threading
import time

# Data structure
from queue import Queue

from .ELog import ELog

_ETMLogger = ELog("EUTILS::ETaskManager")

class ETask():

    __mMaxWaitTime = 0x4554 # ET

    def __init__(self, inPort=None, outPort=None):
        self.__mInPort = inPort
        self.__mOutPort = outPort

    def etask(self):
        raise Exception("etask method not implement...")

    def start(self):
        self.etask()

    def inPortMsgNumbers(self):
        if self.__mInPort:
            return self.__mInPort.qsize()
        return 0

    def outPortMsgNumbers(self):
        if self.__mOutPort:
            return self.__mOutPort.qsize()
        return 0

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
                _ETMLogger.warn("%s receive msg timeout." % str(self))
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


class _ETaskCollector(ETask):

    def __init__(self):
        super().__init__()
        self._enableInPort()

    def etask(self):
        _ETMLogger.debug("Start ETask Collector")
        releaseTaskCnt = 0
        while True:


            releaseQ = Queue()

            while self.inPortMsgNumbers() > 0:
                releaseTaskCnt += 1

                task = self._receiveMsg()
                
                _ETMLogger.debug("[%d] TC Start Release %s" % (releaseTaskCnt, str(task)))
                
                task._alive = False
                task._task = None
                task.wake()
                
                releaseQ.put(task)

            if not releaseQ.empty():
                self.__releaseETaskResource(releaseQ)
                _ETMLogger.debug("[%d] TC Release over" % releaseTaskCnt)
            
            time.sleep(1)

        _ETMLogger.error("End ETask Collector")
                
    
    def __releaseETaskResource(self, releaseQ):

        while not releaseQ.empty():
            task = releaseQ.get()
            maxCheckCnt = 10
            while task.isAlive() and maxCheckCnt > 0:
                time.sleep(1)
                maxCheckCnt -= 1
            del task


# user should not to use it directly, but to implement ETask
class _ETask(threading.Thread):

    def __init__(self, task=None):
        threading.Thread.__init__(self)
        self._task = task
        # life circle control
        self._alive = True
        self.__event = threading.Event()

    def run(self):

        while self._alive:

            self.__event.clear()
            self.__event.wait()

            _ETMLogger.debug(str(self._task) + ": start")

            try:
                if self._task is not None:
                    self._task._ETask__start()
            except Exception as e:
                _ETMLogger.error(" task %s runtime error, %s" % (str(self._task), str(e)))

            _ETMLogger.debug(str(self._task) + ": end")



    def wake(self):
        _ETMLogger.debug("wake: (event, %s) " % str(self.__event))
        if self.isAlive():
            self.__event.set()
        else:
            _ETMLogger.warn("task %s dead already." % str(self))

    def isSleep(self):
        return not self.__event.is_set()



class ETaskManager(threading.Thread):

    __mLock = threading.Lock()

    def __init__(self, maxTaskNums=5, enableLog=False, logLevel=1):

        threading.Thread.__init__(self)

            # only ETM thread using -- {"startTask ID": "endTask List"}
        self.__mTaskRunList = []
        self.__mDataLinks = {"startTask ID": "endTask List"}

        # thread safe
        self.__mTaskSleepPool = Queue()
        self.__mTaskReadyQueue = Queue()

        # final var
        self.__mMaxTaskNums = maxTaskNums

        self.__mETaskCollector = _ETaskCollector()

        
        if enableLog:
            _ETMLogger.config(logLevel=logLevel)
            _ETMLogger.config(console=enableLog)
            _ETMLogger.start()
        else:
            _ETMLogger.config(logLevel=-1)

        # start TC Task
        self.__addTaskAndStart(self.__mETaskCollector)      

    def run(self):

        while True:
            
            _ETMLogger.debug("run task list(size=%s): %s" % (str(len(self.__mTaskRunList)), str(self.__mTaskRunList)))
            

            try:
                sleepTask = []

                # 1. check/modify task status and transport msg 
                for task in self.__mTaskRunList:

                    self.__msgTransport(task)

                    if task.isSleep():
                        _ETMLogger.debug(str(task) + ":" + str(task._task) + " to sleepQ")
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

            except Exception as e:
                
                _ETMLogger.error("ETManager error, you could submit a issue to github page of EasyUtils [%s]" % str(e))
                

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

                _ETMLogger.debug("task usecase: " + str(tasks))

                for task in tasks:
                    self.addTask(taskPre, task)
                    taskPre = task

    def addTask(self, tPre, tNext=None):
        if tPre is None and tNext is None:
            _ETMLogger.error("type is <None, None>, add task: <%s, %s> failed" % (str(tPre), str(tNext)))
            return
        elif tPre is None:
            tPre, tNext = tNext, tPre
        self.__mTaskReadyQueue.put([tPre, tNext])
        _ETMLogger.debug("add task: <%s, %s> to readyQ" % (str(tPre), str(tNext)))


    def __getInPort(self, etask):
        if etask and hasattr(etask, '_ETask__mInPort'):
            return etask._ETask__mInPort
        return None

    def __getOutPort(self, etask):
        if etask and hasattr(etask, '_ETask__mOutPort'):
            return etask._ETask__mOutPort
        return None

    def __trypStartNewETask(self):
        while not self.__mTaskReadyQueue.empty():

            try:
                taskPair = self.__mTaskReadyQueue.get(timeout=1)
            except Exception as e:
                _ETMLogger.warn(str(e))
                break
            
            _ETMLogger.debug("try start new task: %s" % (str(taskPair)))

            if self.runTaskNums() + 2 <= self.__mMaxTaskNums:
                self.__addTaskAndStart(taskPair[0], taskPair[1])

            elif self.runTaskNums() + 1 <= self.__mMaxTaskNums and (id(taskPair[0]) in self.__mDataLinks or id(taskPair[1]) in self.__mDataLinks):
                self.__addTaskAndStart(taskPair[0], taskPair[1])

            else:
                self.__mTaskReadyQueue.put(taskPair)
                break


    def __addTaskAndStart(self, tPre, tNext=None):

        _ETMLogger.debug("start task: <%s, %s>" % (str(tPre), str(tNext)))
        
        _etaskPre, PBool = self.__allocAndBindETask(tPre)
        _etaskNext, NBool = self.__allocAndBindETask(tNext)
        
        if _etaskNext and _etaskPre:
            self.__createDataLink(_etaskPre._task, _etaskNext._task)

        if PBool:
            self.__mTaskRunList.append(_etaskPre)
        if NBool:
            self.__mTaskRunList.append(_etaskNext)

    def __msgTransport(self, task):

        _ETMLogger.debug("[%s]: transport msg (sleep: %s)" % (str(task._task), str(task.isSleep())))

        outPort = self.__getOutPort(task._task)

        if outPort is None:
            return

        tList = self.__mDataLinks[id(task._task)]

        if len(tList) == 0:
            return

        while not outPort.empty():
            
            existInPort = False
            
            data = outPort.get()

            for nextTask in tList:
                
                inPort = self.__getInPort(nextTask)

                if inPort:
                    existInPort = True
                    inPort.put(data)
                    _ETMLogger.debug("data flow: %s --(%s)--> %s" % (id(data), id(task._task), id(nextTask)))
                else:
                    _ETMLogger.warn("src %s --> dst %s, not found inport in dst" % (str(task._task), str(nextTask)))

            if not existInPort:
                _ETMLogger.warn("[Bug?] src %s --> dst %s, not found inport in dst task list" % (str(task._task), str(tList)))
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

        _ETMLogger.debug("Bind task %s to etask %s " % (id(task), id(_etask)))

        if _etask.isSleep():
            _etask.wake()
        else:
            raise

        return _etask, True

    def __createDataLink(self, src, dst):

        if dst is None or src is None:
        
            _ETMLogger.error("create data link failed: task(dst/src) is None.")

        if id(src) in self.__mDataLinks:

            if dst not in self.__mDataLinks[id(src)]:
                self.__mDataLinks[id(src)].append(dst)
            else:
                _ETMLogger.warn("task already exist: <%s, %s>" % (str(src), str(dst)))
        
        else:

            self.__mDataLinks[id(src)] = [ dst ]

        if id(dst) not in self.__mDataLinks:
            self.__mDataLinks[id(dst)] = []
        
        _ETMLogger.debug("create data link: [%s --> %s]" % (id(src), id(dst)))


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

            # release ETask (~ 1/4)
            if cacheProcessNums % 4:
                self.__mTaskSleepPool.put(task)
            else:
                self.__releaseETask(task)

            cacheProcessNums -= 1

    def __TC(self):

        while self.runTaskNums() / 2 + 1 < self.__mTaskSleepPool.qsize():
            task = self.__mTaskSleepPool.get()
            self.__releaseETask(task)
            

    def __releaseETask(self, task):

        self.__getInPort(self.__mETaskCollector).put(task)

            

if __name__ == "__main__":

    print("Hello ETask")
