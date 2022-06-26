'''
Author: SPeak
Date: 2022-05-03 17:40:26
LastEditors: SPeak
LastEditTime: 2022-05-04 18:02:07
FilePath: /EasyUtils/src/test/MyTestTask.py
Description: 
 
'''
from src.eutils import ETask
from src.eutils import getLogger

_EUTestLogger = getLogger("EUtils-Test", logLevel=3, console=False, autoCreateLogFile=True)

class WTask(ETask):

    def __init__(self):
        super().__init__()
        self._enableOutPort()

    def etask(self):
        i = 0
        while i < 5:
            msg = "hello task " + str(i)
            _EUTestLogger.debug(str(self) + " send: " + msg)
            self._sendMsg(msg)
            i = i + 1
        _EUTestLogger.debug("WTask(%s) over" % str(self))

class RTask(ETask):

    def __init__(self):
        super().__init__()
        self._enableInPort()
        self.__MsgCnt = 0

    def etask(self):
        while True:
            try:
                msg = self._receiveMsg(maxWaitTime=5)
                self.__MsgCnt += 1
            except:
                _EUTestLogger.debug("\n<------------stop task %s ----- msg cnt %d --------->\n" % (str(self), self.__MsgCnt))
                break
            _EUTestLogger.debug(msg)

class RWTask(ETask):

    def __init__(self):
        self._enableInPort()
        self._enableOutPort()

    def etask(self):
        i = 0
        while i < 5:
            try:
                msg = self._receiveMsg()
            except Exception as e:
                _EUTestLogger.debug("\n<------------stop task %s -------------->\n" % str(self))
                break
            _EUTestLogger.debug(str(msg) + "(%s)" % str(self))
            self._sendMsg(msg)
            i = i + 1
