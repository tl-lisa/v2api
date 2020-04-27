#mileston20 重置mail發送次數#924(/api/v2/cs/email/reset):
# 綁定會送mail, 註冊會送mail, 重置密碼會送mail;但註冊不限制次數。故不比對mail是否已綁定
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

def emailReg(emailAddr, PWD):
    url = '/api/v2/identity/register/email/send'
    body = {
                'email': emailAddr,
                'password': PWD
            }
    res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body)   
    restext = json.loads(res.text)     
    tempToken = restext['data']['tmpToken']
    sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    actCode = result[0][0]
    url = '/api/v2/identity/register/email/activate'
    body = {
            "tmpToken": tempToken,
            "activateCode": actCode,
            "pushToken": "dshfklkrxkeiyegrkldfkhgdkfasd"
        }
    api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body) 

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])
    emailReg('lisa@truelovelive.dev', '123456')
    
def sendMail(sendTimes, url, body):
    header =  {'Content-Type': 'application/json'}
    if 'binding' in url:
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
    for i in range(sendTimes):
        res = api.apiFunction(test_parameter['prefix'], header, url, 'post', body) 
    return res.status_code

#isSendMail, url, scenario, token, nonce, expected
testData = [
    (True, '/api/v2/identity/binding/email/send', 'testAuth', 'tlqa20200313@gmail.com', 'user_token', 'user_nonce', 4),
    (False, None, 'testAuth', 'tlqa20200313@gmail.com', 'broadcaster_token', 'broadcaster_nonce', 4),
    (False, '/api/v2/identity/binding/email/send', 'happy casd of binding email', 'tlqa20200313@gmail.com', 'backend_token', 'backend_nonce', 2),
    (True, '/api/v2/identity/password/send', 'happy case of reset password', 'lisa@truelovelive.dev', 'liveController1_token', 'liveController1_nonce', 2)
]

'''
驗證只有role=business admim(admin)/ liveController可以reset
reset成功後同mail可以再寄送
reset的mail錯誤
'''
body1 = {}
@pytest.mark.parametrize("isSendMail, url, scenario, email, token, nonce, expected", testData)
def testResetEmailCounter(isSendMail, url, scenario, email, token, nonce, expected):
    header = {'Connection': 'Keep-alive'}
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]
    urlName = '/api/v2/cs/email/reset'
    if isSendMail:
        if 'binding' in url:
            body = {
                'email': email
            }
        elif 'password' in url:
               body = {
                "source": 'email',
                "identifier": email
            }
        sendMail(3, url, body)
    body = {"emails": email}
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    assert res.status_code // 100 == expected
    if expected == 2:
        if 'binding' in url:
            body = {
                'email': email
            }
        elif 'password' in url:
               body = {
                "source": 'email',
                "identifier": email
            }
        assert sendMail(1, url, body) // 100 == 2