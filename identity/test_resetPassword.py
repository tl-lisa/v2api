#milestone120 密碼重置 #911(/api/v2/identity/password/reset)
import json
import requests
import pymysql
import pytest
import time
import string
from datetime import datetime, timedelta
from ..assistence import dbConnect
from ..assistence import initdata
from ..assistence import api
from pprint import pprint
 
env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)

def teardown_module():
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce'] 
    urlName = '/api/v2/identity/password/reset'
    body = {
            "newPassword": "123456",
            "newPasswordConfirm": "123456"
        }
    api.apiFunction(test_parameter['prefix'], header, urlName, 'patch', body)

#codition, token, nonce, PWD, expected
testData = [
    ('pwdFormat', 'user_token', 'user_nonce', ['1234', '123456789012345678901', '123嗨', '123!4', '12 34', '1234😄', '!@！1'], [4, 4, 4, 4, 4, 4, 4]),
    ('pwdNotMatch', 'user_token', 'user_nonce', ['1234a'], [4]),
    ('authFailed', 'err_token', 'err_nonce', ['1234a'], [4]),
    ('happyCase', 'user_token', 'user_nonce', ['1234a'], [2])
]

'''
測試案例：
．password長度要大於等於5，小於等於20
．設定的密碼與確認密碼要一致
．要找得到正確的人
．可以正確更改密碼,並執行登入
'''
@pytest.mark.parametrize("codition, token, nonce, PWD, expected", testData)
def testResetPassword(codition, token, nonce, PWD, expected):
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce] 
    urlName = '/api/v2/identity/password/reset'
    for i in range(len(PWD)):
        if codition == 'pwdNotMatch':
            body = {
                "newPassword": PWD[i],
                "newPasswordConfirm": "Tl0214Hello"
            }
        else:
            body = {
                "newPassword": PWD[i],
                "newPasswordConfirm": PWD[i]
            }
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'patch', body)
        assert res.status_code // 100 == expected[i]
        if codition == 'happyCase':
            urlName = '/api/v2/identity/auth/login'
            body = {
                "account": test_parameter['user_acc'],
                "password": PWD[i],
                "pushToken": "pwdkusaoxcjfoiakfjosaidjf"
            }
            res = api.apiFunction(test_parameter['prefix'], '{"Content-Type": "application/json"}', urlName, 'post', body)
            assert res.status_code // 100 == 2
