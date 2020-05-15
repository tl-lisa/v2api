#milestone19 #860解除第3方綁定；必要條件：該帳號需已綁定email
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import lineLogin
from pprint import pprint

env = 'QA'
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
    emailReg('lisa@gmail.com', '123456')


def getTestData():
    testData = [
        ('lineLogin', 4),
        ('tokenWrong', 4),
        ('nonceWrong', 4),
        ('bindEmail', 2),
        ('accountLogin', 4),
        ('emailLogin', 4)
    ]
    return(testData)

def loginWithLine():
    url = '/api//v2/3rdParty/line/verify'
    idToken, accessToken = (lineLogin.line_login())
    body = {
        'accessToken': accessToken,
        'idToken': idToken
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])

def loginV2(account, pwd):
    url = '/api/v2/identity/auth/login'
    body = {
        "account": account,
        "password": pwd,
        "pushToken": 'dshfklkrjhjayegrkldfkhgdkfasd'
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])

def bindMail(auth):
        head = {'Content-Type': 'application/json', 'X-Auth-Token': '', 'X-Auth-Nonce': '', 'Authorization': ''}
        head['X-Auth-Token'] = auth[0]
        head['X-Auth-Nonce'] = auth[1]
        head['Authorization'] = auth[2]
        url = '/api/v2/identity/binding/email/send'
        body = {
            'email': 'lisa123@gmail.com'
        }
        api.apiFunction(test_parameter['prefix'], head, url, 'post', body)    
        sqlStr = "select activate_code from identity_email_bind_history where id = (select max(id) from identity_email_bind_history)"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        url ='/api/v2/identity/binding/email/activate'
        body = {
            "source": "advance",
            "email": 'lisa123@gmail.com',
            "password": '123456',
            "activateCode": actCode
        }
        api.apiFunction(test_parameter['prefix'], head, url, 'post', body)


'''
・尚未綁定email即要執行revoke
・正確的token/nonce但非第3方登入帳號（含email；含account)
・已綁定email，且正確的token/nonce執行解除
'''
class TestRevoke():
    lineAuth = []
    @pytest.mark.parametrize("condition, excepted", getTestData())
    def testThirdRevoke(self, condition, excepted):
        url = '/api/v2/3rdParty/revoke'
        head = {'X-Auth-Token': '', 'X-Auth-Nonce': '', 'Authorization': ''}
        if condition == 'lineLogin':
            token, nonce, idToken = loginWithLine()
            self.lineAuth.extend([token, nonce, idToken])
        elif condition == 'tokenWrong':
            token = '1235'
            nonce = self.lineAuth[1]
            idToken = self.lineAuth[1]
        elif condition == 'nonceWrong':
            token = self.lineAuth[0]
            nonce = '1234'
            idToken = self.lineAuth[0]
        elif condition == 'bindEmail':
            bindMail(self.lineAuth)
            token = self.lineAuth[0]
            nonce = self.lineAuth[1]
            idToken = self.lineAuth[1]
        elif condition == 'accountLogin':
            token, nonce, idToken = loginV2('track0012', '123456')
        elif condition == 'emailLogin':
            token, nonce, idToken = loginV2('lisa@gmail.com', '123456')
        head['X-Auth-Token'] = token
        head['X-Auth-Nonce'] = nonce
        head['Authorization'] = idToken
        res =  api.apiFunction(test_parameter['prefix'], head, url, 'delete', None)
        assert res.status_code // 100 == excepted