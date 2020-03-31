#milestone19 #858 Line login 用line順便驗證第3方登入的流程
import json
import requests
import pymysql
import pytest
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import lineLogin
from pprint import pprint

env = 'testing'
test_parameter = {}


def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])

def getTestData():
    #condition, expected
    testData = [
        ('firstLogin', 2),
        ('secondLogin', 2),
        ('accToken_Wrong', 4),
        ('idToken_Wrong', 4),
        ('expired', 4)
    ]
    return testData

class TestLineLogin():
    auth = []
    '''
    ・第一次用line登入建立帳號，會導到email綁定頁面
    ・第二次用line登入，則不會導到email綁定頁面
    ・access token錯誤，登入失敗
    ・id token錯誤。登入失敗
    ・資訊皆正確，但access token expired，登入失敗
    '''
    @pytest.mark.parametrize("condition, expected", getTestData())
    def testlineFlow(self, condition, expected):
        url = '/api/v2/3rdParty/line/verify'
        if condition == 'firstLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.extend([idToken, accessToken])
        elif condition == 'secondLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.extend([idToken, accessToken])
        elif condition == 'accToken_Wrong':
            body = {
                'accessToken': 'sUpdewDer123Oi',
                'idToken': idToken[1]
            }
        elif condition == 'idToken_Wrong':
            body = {
                'accessToken': self.auth[1],
                'idToken': 'aBcdoeiDp'
            }
        elif condition == 'expired':
            body = {
                'accessToken': self.auth[0],
                'idToken': idToken[0]
            }
        res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
        assert res.status_code == expected
        if condition == 'firstLogin':
            restext = json.loads(res.text)
            assert restext['data']['isNew'] == 1
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
        if condition == 'secondLogin':
            assert restext['data']['isNew'] == 0
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
        