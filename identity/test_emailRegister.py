import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import setting as mysetting
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from python_settings import settings

settings.configure(mysetting) 

'''
email註冊：
1.一週同email限制發送3次
2.同IP不同email一迥限制發送3次
3.已註冊成功的email要求發送會錯誤
4.已綁定的email要求發送會錯誤
'''
class TestSendEmail():
    pass


'''
啟用active code:
1.temptoken與active code不match
2.active code已經expired
3.active code錯誤
4.temptoken與active code皆正確
'''
class TestActivateCode():
    pass

