#milestone 19 #919
import json
import requests
import pymysql
import time
import pytest
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import setting as mysetting
from ..assistence import lineLogin
from python_settings import settings
from pprint import pprint

env = 'testing'
test_parameter = {}
#header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    head = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['backend_token'], 'X-Auth-Nonce': test_parameter['backend_nonce']}
    id = api.search_user(test_parameter['prefix'], 'track0005', head)
    api.change_user_mode(test_parameter['prefix'], id, '1', head)


def getTestData():
    #isSuspended, account, pwd, pushToken, expected
    TestData = [
        (False, 'track0005', '123456', 'dshfklkrjhjayegrkldfkhgdkfasd', 2),
        (False, 'lisa@gmail.com', '123456', 'dshfklkrjhjayegrkldfkhgdkfasd', 2),
        (False, 'lisa', '123456', 'dshfklkrjhjayegrkldfkhgdkfasd', 4),
        (False, 'track0005', '123', 'dshfklkrjhjayegrkldfkhgdkfasd', 4),
        (False, '', '123456', 'dshfklkrjhjayegrkldfkhgdkfasd', 4,),
        (False, 'track0005', '123456', '', 2),
        (True, 'track0005', '123456', 'dshfklkrjhjayegrkldfkhgdkfasd', 4)
    ]
    return (TestData)

class TestV2Login():
    '''
    測試狀況：
    使用正確的帳號密碼登入
    使用正確的email密碼登入
    使用不正確的帳號密碼登入
    帳號密號空白
    未給pushtoken
    帳號被停權
    '''

    def suspendAccount(self, account):
        head = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['backend_token'], 'X-Auth-Nonce': test_parameter['backend_nonce']}
        id = api.search_user(test_parameter['prefix'], account, head)
        api.change_user_mode(test_parameter['prefix'], id, '-2', head)

    @pytest.mark.parametrize("isSuspended, account, pwd, pushToken, expected", getTestData())
    def testLogin(self, isSuspended, account, pwd, pushToken, expected):
        head = {'Content-Type': 'application/json'}
        url = test_parameter['prefix'] + '/api/v2/identity/auth/login'
        body = {
            "account": account,
            "password": pwd,
            "pushToken": pushToken
        }
        self.suspendAccount(account) if isSuspended else None
        res = requests.post(url, headers=head, json=body) 
        assert res.status_code == expected
        if expected == 2:
            url = test_parameter['prefix'] + '/api//v2/identity/myInfo'
            restext = json.loads(res.text)
            head['X-Auth-Token'] = restext['data']['token']
            head['X-Auth-Nonce'] = restext['data']['nonce']
            head['Authorization'] = restext['data']['idToken']
            del head['Content-Type']
            res = requests.get(url, headers=head)
            restext = json.loads(res.text)
            assert restext['data']['loginId'] == account

