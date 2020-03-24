import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import setting as mysetting
from ..assistence import lineLogin
from python_settings import settings
from pprint import pprint

#settings.configure(mysetting)

'''
1.第一次用line登入建立帳號，會導到email綁定頁面
2.第二次用line登入，則不會導到email綁定頁面
3.access token錯誤，登入失敗
4.id token錯誤。登入失敗
5.資訊皆正確，但access token expired，登入失敗
6.access token, id token皆正確應登入成功，且第3方登主與帳號自動綁定
'''
class TestLineLogin():
    url = 'https://www.googleapis.com/gmail/v1/users/' + settings.email + '/messages/1'
    res = requests.get(url)
    print(res.status_code)
    print(json.loads(res.text))