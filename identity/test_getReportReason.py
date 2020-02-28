import json
import requests
import time
import string
from ..assistence import api
from ..assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
idList = []
createTime = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)


class TestgetReportReason():
    apiName = '/api/v2/identity/inform/reason'
    def testUserGetReason(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 7

    def testLivemasterGetReason(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 7

    def testAdminGetReason(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 7

    def testWithoutAuth(self):
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']                      
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'get', '')
        assert res.status_code // 100 == 4
