'''
Author: SPeak
Date: 2022-05-04 19:44:47
LastEditors: SPeak
LastEditTime: 2022-05-04 19:57:48
FilePath: /EasyUtils/demo/helloElog.py
Description: 

'''

from eutils import getLogger

el = getLogger("EUtils", logLevel=4)

el.info("Hello ELog")
