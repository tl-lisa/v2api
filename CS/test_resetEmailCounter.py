#mileston20 重置mail發送次數#924(/api/v2/cs/email/reset)
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

def setup_module():
    initdata.set_test_data(env, test_parameter)
    
def sendMail(emailAddr, sendTimes):
    url = '/api/v2/identity/register/email/send'
    body = {
        'email': emailAddr,
        'password': '123456'
    }
    for i in range(sendTimes):
        res = api.apiFunction(test_parameter['prefix'], '', url, 'post', body) 
    return res.status_code

#isSendMail, scenario, token, nonce, expected
testData = [
    (True, 'testAuth', 'user_token', 'user_nonce', 4),
    (False, 'testAuth', 'broadcaster_token', 'broadcaster_nonce', 4),
    (False, 'wrongMail', 'backend_token', 'backend_nonce', 4),
    (False, 'testAuth', 'backend_token', 'backend_nonce', 2),
    (True, 'testAuth', 'liveController1_token', 'liveController1_nonce', 2)
]

'''
驗證只有role=business admim(admin)/ liveController可以reset
reset成功後同mail可以再寄送
reset的mail錯誤
'''
@pytest.mark.parameterize("isSendMail, scenario, token, nonce, expected", testData)
def testResetEmailCounter(isSendMail, scenario, token, nonce, expected):
    header = {'Connection': 'Keep-alive'}
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]
    urlName = '/api/v2/cs/email/reset'
    if isSendMail:
        sendMail('lisa@truelovelive.dev', 3)
    if scenario == 'wrongMail':
        body = {"emails": "lisa@truelove.dev"}
    else:
        body = {"emails": "lisa@truelovelive.dev"}
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    assert res.status_code // 100 == expected
    if expected == 2:
        assert sendMail('lisa@truelovelive.dev', 1) // 100 == 2