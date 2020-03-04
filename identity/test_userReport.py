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
idlist = []
createTime = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))


class TestReportPost():
    body = {'postId': 0, 'reason': 1}
    apiName = '/api/v2/identity/inform'
    postId = 0
    def setup_class(self):
        apiName = '/api/v2/identity/track'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        body = {"liveMasterId": idlist[0]}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/identity/track/photoPost?item=10&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)        
        self.postId = restext['data'][0]['id'] if restext['totalCount'] > 0 else None

    def teardown_class(self):
        apiName = '/api/v2/identity/track/' + idlist[0]
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)

    def testReportPost(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['postId'] = self.postId     
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 2

    def testReportPostNotExist(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['postId'] = 0    
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testReportWithoutAuth(self):
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']    
        self.body['postId'] = self.postId     
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testReportWrongReason(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['reason'] = 0   
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4    
    
    def testParameterWrong(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body.pop('reason')  
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4    

class TestReportLivemaster():
    body = {'liveMasterId': 'abc', 'reason': 1}
    apiName = '/api/v2/identity/inform'
    def testReportLivemaster(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['liveMasterId'] = idlist[0]
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 2

    def testReportLivemasterIDNotExist(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['liveMasterId'] = '123498arfosrl'
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testReportWithoutAuth(self):
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']    
        self.body['liveMasterId'] = idlist[0]
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testReportIsNotLivemaster(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        self.body['liveMasterId'] = idlist[1]
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testReportWrongReason(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body['reason'] = 0
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4

    def testParameterWrong(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        self.body.pop('reason')  
        res = api.apiFunction(test_parameter['prefix'], header, self.apiName, 'post', self.body)
        assert res.status_code // 100 == 4    
