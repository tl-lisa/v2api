#milestone 19 新增動態贈禮通知設定
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def getTestData():
    #token, nonce, condition, body, expected
    testData = [
        ('broadcaster_token', 'broadcaster_nonce', '', '', {'status': 2, 'comment': True, 'track': True, 'live': True, 'postGift': True}),
        ('broadcaster_token', 'broadcaster_nonce', 'changeRole', '', {'status': 2, 'comment': False, 'track': False, 'live': True, 'postGift': False}),
        ('broadcaster_token', 'broadcaster_nonce', 'setting', {'comment': False, 'track': False, 'live': False, 'postGift': False}, {'status': 2, 'comment': False, 'track': False, 'live': False, 'postGift': False}),
        ('user_token', 'user_nonce', '', '', {'status': 2, 'comment': False, 'track': False, 'live': True, 'postGift': False}),
        ('user_token', 'user_nonce', 'setting', {'comment': False, 'track': False, 'live': True, 'postGift': True}, {'status': 2, 'comment': False, 'track': False, 'live': True, 'postGift': True}),
        ('user_token', 'user_nonce', 'setting', {'comment': False, 'track': False, 'live': False}, {'status': 2, 'comment': False, 'track': False, 'live': False, 'postGift': True}),
        ('user_token', 'user_nonce', 'setting', {'comment': False, 'track': False, 'live': True, 'postGift': None}, {'status': 2, 'comment': False, 'track': False, 'live': True, 'postGift': True}),
        ('err_token', 'err_nonce', 'setting', {'comment': False, 'track': False, 'live': True, 'postGift': True}, {'status': 4}),
        ('user_token', 'user_nonce', 'setting', {}, {'status': 4})
    ]
    return testData

'''
・直播主首次預設皆為true;一般user只有live是true
・token/nonce錯誤
・body為空值
・body內key值不存在
・body內有key無value
'''
class TestNotificationSetting():
    mid = ''
    def changeRole(self, roleType):
        header['Content-Type'] = 'application/json'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        changelist = [self.mid]  
        api.change_roles(test_parameter['prefix'], header, changelist, roleType) #一般用戶:5;直播主：4

    def setup_class(self):
        sqlList = ['truncate table user_notification_settings']
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        self.mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)   
        changelist = [self.mid]  
        api.change_roles(test_parameter['prefix'], header, changelist, 4) #一般用戶:5;直播主：4

    @pytest.mark.parametrize("token, nonce, condition, body, expected", getTestData())
    def testSetting(self, token, nonce, condition, body, expected):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiNmae = '/api/v2/identity/notifySetting'
        if condition == 'changeRole':
            self.changeRole('5')       
        elif condition == 'setting':
            res = api.apiFunction(test_parameter['prefix'], header, apiNmae, 'post', body)
            assert res.status_code // 100 == expected['status']
        if expected['status'] == 2:
            res = api.apiFunction(test_parameter['prefix'], header, apiNmae, 'get', None)
            restext = json.loads(res.text)
            restext['data']['comment'] == expected['comment']
            restext['data']['track'] == expected['track']
            restext['data']['live'] == expected['live']
            restext['data']['postGift'] == expected['postGift']
        if condition == 'changeRole':
            self.changeRole('4')       
