#milestone19 V2取得，修改個人資訊 #863
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
from ..assistence import lineLogin
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])

def regByMail():
    url = '/api/v2/identity/register/email/send'
    body = {
                'email': 'tl-lisa@truelove.dev',
                'password': '12345'
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
    res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body) 
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])    

def loginByLine():
    url = '/api/v2/3rdParty/line/verify'
    idToken, accessToken = (lineLogin.line_login())
    body = {
        'accessToken': accessToken,
        'idToken': idToken
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])    

def loginByAccount():
    url = '/api/v2/identity/auth/login'
    body = {
        "account": "track0005",
        "password": "123456",
        "pushToken":"dshfklkrjhjayegrkldfkhgdkfasd"
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body) 
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])

def getData(testName):
    if testName == 'getInfo':
        #token, nonce, account, role, expected
        testData = [
            ('user_token', 'user_nonce', 'user_acc', 5, 2),
            ('broadcaster_token', 'broadcaster_nonce', 'broadcaster_acc', 4, 2),
            ('backend_token', 'backend_nonce', 'backend_acc', 7, 2),
            ('liveController1_token', 'liveController1_nonce', 'liveController1_acc', 10, 2),
            ('err_token', 'err_nonce', '', '', 4)
        ]
    if testName == 'updateInfo':
        #token, nonce, keyInfo, valueInfo, expected
        testData = [
            ('user_token', 'user_nonce', 'nickname', '  ', 4),
            ('user_token', 'user_nonce', 'nickname', '🥰5566　-🥰', 2),
            ('user_token', 'user_nonce', 'nickname', 'AB歡樂派！', 2),
            ('user_token', 'user_nonce', 'sex', '2', 2),
            ('user_token', 'user_nonce', 'isPublicSexInfo', False, 2),
            ('user_token', 'user_nonce', 'description', '哈， I am richman!！！😂 😂 ', 2),
            ('user_token', 'user_nonce', 'description', '', 2),
            ('user_token', 'user_nonce', 'birthday', int(time.time()), 2),
            ('user_token', 'user_nonce', 'birthday', 0, 2)
        ]
    elif testName == 'newUser':
        #condition, expected
        testData = [
            ('regByMail', 2),
            ('loginByLine', 2)
        ]
    return testData

'''
・檢測token/nonce取得對應帳號
'''
@pytest.mark.skip()
class TestGetMyInfo():
    @pytest.mark.parametrize("token, nonce, account, role, expected", getData('getInfo'))
    def testGetInfo(self, token, nonce, account, role, expected):
        url = '/api/v2/identity/myInfo'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, url, 'get', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['data']['roles'][0]['id'] == role
            assert restext['data']['loginId'] == test_parameter[account]

'''
・token/nonce判斷
・新註冊帳號新增對應資料
    isPasswordSet
    verifiedEmail
    verifiedPhone
    3rdPartySource
    3rdPartyInfo
・舊有帳號可以修改資料，若是空白則修改成空白
'''

class TestUpdateMyinfo():
    @pytest.mark.skip()
    @pytest.mark.parametrize("condition, expected", getData('newUser'))
    def testNewAccount(self, condition, expected):
        url = '/api/v2/identity/myInfo'
        if condition == 'regByMail':
            token, nonce, idToken = regByMail()
            header['X-Auth-Token'] = token
            header['X-Auth-Nonce'] = nonce
            header['Authorization'] = idToken
        elif condition == 'loginByLine':
            token, nonce, idToken = loginByLine()
            header['X-Auth-Token'] = token
            header['X-Auth-Nonce'] = nonce
            header['Authorization'] = idToken
        time.sleep(2)
        res = api.apiFunction(test_parameter['prefix'], header, url, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        if condition == 'regByMail':
            assert restext['isPasswordSet'] == True
            assert restext['verifiedEmail'] == 'tl-lisa@truelove.dev'
        elif condition == 'loginByLine':
            assert restext['3rdPartySource'] == 'line'
            print(restext['3rdPartyInfo'])
    #@pytest.mark.skip()
    @pytest.mark.parametrize("token, nonce, keyInfo, valueInfo, expected", getData('updateInfo'))
    def testUpdateInfo(self, token, nonce, keyInfo, valueInfo, expected):
        body = {'nickname': '123', 'sex': 1, 'isPublicSexInfo': True, 'description': 'haha', 'birthday': int(time.time() - 5000)}
        url = '/api/v2/identity/myInfo'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        body[keyInfo] = valueInfo
        #print(body)
        res = api.apiFunction(test_parameter['prefix'], header, url, 'put', body)
        time.sleep(5)
        res = api.apiFunction(test_parameter['prefix'], header, url, 'get', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert restext['data'][keyInfo] == valueInfo
            if keyInfo == 'isPasswordSet' and valueInfo == True:
                assert restext['data']['sex'] is None