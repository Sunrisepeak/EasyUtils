'''
Author: SPeak
Date: 2022-05-03 17:40:26
LastEditors: SPeak
LastEditTime: 2022-05-03 22:51:19
FilePath: /EasyUtils/src/test/MyTestTask.py
Description: 
 
'''
from src.eutils import ETask


class WTask(ETask):

    def __init__(self):
        self._enableOutPort()

    def etask(self):
        i = 0
        while i < 5:
            self._sendMsg("hello task " + str(i))
            i = i + 1
        print("WTask(%s) over" % str(self))

class RTask(ETask):

    def __init__(self):
        self._enableInPort()

    def etask(self):
        while True:
            try:
                msg = self._receiveMsg(maxWaitTime=10)
            except:
                print("\n<------------stop task %s -------------->\n" % str(self))
                break
            print(msg)

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
                print("\n<------------stop task %s -------------->\n" % str(self))
                break
            print(str(msg) + "(%s)" % str(self))
            self._sendMsg(msg)
            i = i + 1
