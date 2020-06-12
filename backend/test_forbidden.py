#milestone24 後台禁詞功能 #1312～1316（新增，編輯，查詢及刪除);允許有重複的禁詞
import json
import requests
import pymysql
import pytest
import time
import string
from datetime import datetime, timedelta
from assistence import dbConnect
from assistence import initdata
from assistence import api
from assistence import sundry
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
fid = 0

def setup_module():
    initdata.set_test_data(env, test_parameter)  
    sqlList = ["truncate table forbidden", "alter table forbidden auto_increment = 1"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)

def getTestData():
    #scenario, token, nonce, isReset, funName, way, id, words, item, page, totalCount, expected
    #排除新增字元太長的case；編輯時給錯誤的id；刪除時給錯誤的id
    testData = [
        ('correct auth, add forbidden', 'backend_token', 'backend_nonce', False, 'add', 'post', 0, '代購1000', 1, 1, 0, 2),
        ('correct auth, forbidden duplicate', 'backend_token', 'backend_nonce', False, 'add', 'post', 0, '代購1000', 1, 1, 0, 2),
        ('correct auth, add forbidden ', 'backend_token', 'backend_nonce', False, 'add', 'post', 0, 'TMD 🤬', 1, 1, 0, 2),
        ('wrong auth', 'liveController1_token', 'liveController1_nonce', False, 'add', 'post', 0, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'broadcaster_token', 'broadcaster_nonce', False, 'add', 'post', 0, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'user_token', 'user_nonce', False, 'add', 'post', 0, '代購1000', 1, 1, 0, 4),
        ('correct auth, edit forbidden', 'backend_token', 'backend_nonce', True, 'edit', 'patch', 1, '代購500', 1, 1, 0, 2),
        ('wrong auth', 'liveController1_token', 'liveController1_nonce', False, 'edit', 'patch', 1, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'broadcaster_token', 'broadcaster_nonce', False, 'edit', 'patch', 1, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'user_token', 'user_nonce', False, 'edit', 'patch', 1, '代購1000', 1, 1, 0, 4),
        ('correct auth, get all forbidden, page=1', 'backend_token', 'backend_nonce', True, 'all', 'get', 0, '代購1000', 1, 1, 3, 2), 
        ('correct auth, get all forbidden, page=2', 'backend_token', 'backend_nonce', False, 'all', 'get', 0, '代購1000', 1, 2, 3, 2),
        ('wrong auth', 'liveController1_token', 'liveController1_nonce', False, 'all', 'get', 0, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'broadcaster_token', 'broadcaster_nonce', False, 'all', 'get', 0, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'user_token', 'user_nonce', False, 'all', 'get', 0, '代購1000', 1, 1, 0, 4),
        ('correct auth, get single forbidden', 'backend_token', 'backend_nonce', True, 'single', 'get', 1, '代購1000', 1, 1, 0, 2),
        ('wrong auth', 'liveController1_token', 'liveController1_nonce', False, 'single', 'get', 1, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'broadcaster_token', 'broadcaster_nonce', False, 'single', 'get', 1, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'user_token', 'user_nonce', False, 'single', 'get', 1, '代購1000', 1, 1, 0, 4),
        ('correct auth, delete forbidden', 'backend_token', 'backend_nonce', True, 'del', 'delete', 1, '代購1000', 1, 1, 0, 2),
        ('correct auth, get delete forbidden', 'backend_token', 'backend_nonce', False, 'single', 'get', 1, '代購1000', 1, 1, 0, 2),
        ('wrong auth', 'liveController1_token', 'liveController1_nonce', False, 'del', 'delete', 2, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'broadcaster_token', 'broadcaster_nonce', False, 'del', 'delete', 2, '代購1000', 1, 1, 0, 4),
        ('wrong auth', 'user_token', 'user_nonce', False, 'del', 'delete', 2, '代購1000', 1, 1, 0, 4)
    ]
    return testData


class TestForbidden():
    words = ['初樂粉絲後援會', '點數代儲', '佛地魔']
    
    def addForbidden(self):
        apiName = '/api/v2/backend/forbidden'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {'word': ''}
        for i in self.words:
            body['word'] = i
            api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)

    def reset(self):
        global fid
        fid = 0
        sqlList = ["truncate table forbidden", "alter table forbidden auto_increment = 1"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        self.addForbidden()

    def compareResult(self, fName, result, id, words, totalCount):
        if result == '':
            apiName = '/api/v2/backend/forbidden/' + str(id)
            res  = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
            restext = json.loads(res.text)
            assert restext['data']['id'] == id
            assert restext['data']['word'] == words
        else:
            if type(result['data']) == list:
                for i in result['data']:
                    assert i['id'] == id
                    assert i['word'] == words
            else:
                assert result['data']['id'] == id
                assert result['data']['word'] == words
            if totalCount != 0:
                assert result['totalCount'] == totalCount
        

    @pytest.mark.parametrize("scenario, token, nonce, isReset, funName, way, id, words, item, page, totalCount, expected", getTestData())
    def testBKForbidden(self, scenario, token, nonce, isReset, funName, way, id, words, item, page, totalCount, expected):
        self.reset() if isReset else None
        restext = {}
        fundic = {
            'add': {'apiName': '/api/v2/backend/forbidden', 'body': {'word': words}},
            'edit': {'apiName': '/api/v2/backend/forbidden', 'body': {'id': id, 'word': words}},
            'all': {'apiName': '/api/v2/backend/forbidden/list?' + 'item=' + str(item) + '&page=' + str(page), 'body': None},
            'single': {'apiName': '/api/v2/backend/forbidden/' + str(id), 'body': None},
            'del': {'apiName': '/api/v2/backend/forbidden/' + str(id), 'body': None}
        }
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, fundic[funName]['apiName'], way, fundic[funName]['body'])
        assert res.status_code // 100 == expected
        if  expected == 2:
            global fid
            fid += 1
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok'
            assert restext['Message'] == 'SUCCESS' 
            compareDic = {
                'add': [funName, '', fid, words, 0],
                'edit': [funName, '', id, words, 0],
                'all': [funName, restext,  abs(page - 3) + 1, self.words[abs(page - 3)], totalCount],
                'single':[funName, restext, id, self.words[id - 1], 0]
            }
            if funName != 'del':
                #pprint(restext)
                self.compareResult(compareDic[funName][0], compareDic[funName][1], compareDic[funName][2], compareDic[funName][3], compareDic[funName][4])
            else:
                sqlStr = "select count(*) from forbidden where id = " + str(id) + " and delete_at <> ''" 
                record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                assert record[0][0] == 1
