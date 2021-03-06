#milestone19 #858 Line login 用line順便驗證第3方登入的流程
#milestone22 第3方登入要檢查是否停權 #1158
#milestone23 新註冊用戶未填nickname需自動帶預設值'初樂用戶 ' #1245
import json
import requests
import pymysql
import pytest
import time
import string
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import lineLogin
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])

'''
・第一次用line登入建立帳號，會導到email綁定頁面
・第二次用line登入，則不會導到email綁定頁面
・access token錯誤，登入失敗
・id token錯誤。登入失敗
・資訊皆正確，但帳號已被suspended則無法登入
'''
def getTestData():
    #condition, expected
    testData = [
        ('firstLogin', 2),
        ('secondLogin', 2),
        ('accToken_Wrong', 4),
        ('idToken_Wrong', 4),
        ('suspend', 4)
    ]
    return testData

class TestLineLogin():
    auth = []
    userId = ''
    def teardown_class(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        api.change_user_mode(test_parameter['prefix'], self.userId, 1, header)

    @pytest.mark.parametrize("condition, expected", getTestData())
    def testlineFlow(self, condition, expected):
        url = '/api/v2/3rdParty/line/verify'
        #print('condition=%s'%condition)
        if condition == 'firstLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.append({'idToken': idToken, 'accessToken': accessToken})
        elif condition == 'secondLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.append({'idToken': idToken, 'accessToken': accessToken})
        elif condition == 'accToken_Wrong':
            body = {
                'accessToken': 'sUpdewDer123Oi',
                'idToken': self.auth[1]['idToken']
            }
        elif condition == 'idToken_Wrong':
            body = {
                'accessToken': self.auth[1]['accessToken'],
                'idToken': 'aBcdoeiDp'
            }
        elif condition == 'suspend':
            sqlStr = "select identity_id from identity_third_party where remote_user_id = 'U28ec1317311a7e4da93b5da156a376f4'"
            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
            self.userId = record[0][0]
            api.change_user_mode(test_parameter['prefix'], self.userId, -2, header)
            body = {
                'accessToken': self.auth[1]['accessToken'],
                'idToken': self.auth[1]['idToken']
            }
        res = api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
        assert res.status_code // 100 == expected
        if condition == 'firstLogin':
            restext = json.loads(res.text)
            assert restext['data']['isNew'] == 1
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
            restext = json.loads(res.text)
            sqlStr = "select nickname from identity where token = '" + restext['data']['token'] + "' and  nonce = '" + restext['data']['nonce'] + "'"
            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            assert '初樂用戶 ' in record[0][0]
            time.sleep(10)
        if condition == 'secondLogin':
            restext = json.loads(res.text)
            assert restext['data']['isNew'] == 0
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
        