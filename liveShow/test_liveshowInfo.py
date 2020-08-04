#milestone27 新增開始與結束時間，serverTimeStamp，房主的uuid(這支不管token/nonce)
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import liveshowLib
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
memberList = []
liveshowId = []

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearLiveData(test_parameter['db'])
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'],
    test_parameter['user_acc'], test_parameter['user1_acc']], idList)
    liveshowLib.createMember(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], memberList)
    liveshowLib.liveshowPrepare(test_parameter['prefix'], test_parameter['db'], header, 'TrueLove teams', 2, 0, 2, 3, 351, '', 
    False, False, memberList, liveshowId) 

testData = [
    ('user取得liveshow訊息', 'user_token', 'user_nonce', 'getId', 2),
    ('broadcaster取得liveshow訊息',  'broadcaster_token', 'broadcaster_nonce', 'getId', 2),
    ('backend取得liveshow訊息',  'backend_token', 'backend_nonce', 'getId', 2),
    ('liveshowID為空值',  'broadcaster_token', 'broadcaster_nonce', 'empty', 4),
    ('liveshowID為不存在',  'broadcaster_token', 'broadcaster_nonce', 'wrongId', 4)
]

class TestLiveshowInfo():
    @pytest.mark.parametrize('scenario, token, nonce, action, expected', testData)         
    def test_getInfo(self, scenario, token, nonce, action, expected):
        actionDic = {
            'getId': 'select liveshow_id, title, pool_id from liveshow where id = 1',
            'empty': '',
            'wrongId': 'errId'
        }
        if action == 'getId':
            result = dbConnect.dbQuery(test_parameter['db'], actionDic[action])
            liveshowId = result[0][0]
        else:
            liveshowId = actionDic[action]
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/liveshow/info'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', {'liveshowId': liveshowId})
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert restext['title'] == result[0][1]
            assert restext['masterId'] == result[0][2]
            assert all([len(str(restext['liveStartTime'])) == 10, type(restext['liveStartTime']) == int])
            assert all([len(str(restext['liveEndTime'])) == 10, type(restext['liveEndTime']) == int])
            assert all([len(str(restext['serverTimeStamp'])) == 10, type(restext['serverTimeStamp']) == int])
