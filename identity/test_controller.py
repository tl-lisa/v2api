import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass   


class TestLiveController():
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
        #uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header)
        
    def teardown_class(self):
        #移除場控身份
        #回復直播主身份
        midlist = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)  
        midlist.append(mid)    
        api.change_roles(test_parameter['prefix'], header, midlist, 4)         
        uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header)    
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        delController = '/api/v2/liveMaster/liveController/' + uid
        api.apiFunction(test_parameter['prefix'], header, delController, 'delete', '')        
       
    def testLiveController(self):        
        midlist = []
        apilink = '/api/v2/identity/{{uid}}/role/liveController?item=20&page=1'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
        #非任何人的場控   
        uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header)
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        linkadd = apilink.replace('{{uid}}', uid)
        res = api.apiFunction(test_parameter['prefix'], header, linkadd, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4
        assert restext['Message'] == "User's live controller is not existed."
        #設為場控
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        addController = '/api/v2/liveMaster/liveController'
        body = {"userId": uid}
        res = api.apiFunction(test_parameter['prefix'], header, addController, 'post', body)
        assert int(res.status_code / 100) == 2
        res = api.apiFunction(test_parameter['prefix'], header, linkadd, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert restext['data'][0]['userId'] == mid
        assert restext['totalCount'] == 1
        #直播主變成一般用戶 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
        midlist.append(mid)     
        api.change_roles(test_parameter['prefix'], header, midlist, 5)         
        res = api.apiFunction(test_parameter['prefix'], header, linkadd, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4
        assert restext['Message'] == "User's live controller is not existed."
       
