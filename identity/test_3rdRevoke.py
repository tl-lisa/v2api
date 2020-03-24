import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import setting as mysetting
from pprint import pprint


'''
1.尚未綁定email即要執行revoke
2.錯誤的token/nonce
3.以email註冊未綁定3rd，卻要執行解除
4.已綁定email，且正確的token/nonce執行解除
'''
class TestRevoke():
    pass