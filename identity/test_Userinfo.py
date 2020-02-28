import json
import requests
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
idList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}


def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))    

def teardown_module():
    pass


class TestGetUserInfo():
    apiName = '/api/v2/identity/userInfo/'
    def testGetCSInfo(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + idList[2], 'get', None)
        restext = json.loads(res.text)
        print(self.apiName + idList[2])
        print(type(restext['data']['roles']))
        print(restext['data']['roles'])
        assert res.status_code // 100 == 2        
        assert restext['data']['roles'].find('ROLE_LIVE_CONTROLLER') > 0
    
    def testGetLivemasterInfo(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + idList[0], 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['data']['roles'].find('ROLE_MASTER') > 0

    def testGetAdminInfo(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + idList[1], 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['data']['roles'].find('ROLE_BUSINESS_MANAGER') > 0

    def testWithoutAuth(self):
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + idList[2], 'get', None)
        assert res.status_code // 100 == 4


    def testIdNotExist(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + 'adfpdifjioewokxjoixjdfowe', 'get', None)
        assert res.status_code // 100 == 4

    def testGetUserInfo(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName + idList[4], 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['data']['roles'].find('ROLE_USER') > 0
 