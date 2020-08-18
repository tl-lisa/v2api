#milestone28重構此測試案例
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'], 
                        test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc'], test_parameter['user2_acc']], idList)

@pytest.fixture(scope='class')
def initForCreate():
    initdata.clearAnnouncement(test_parameter['db'])
    initdata.clearFansInfo(test_parameter['db'])
    auth = ['user_token', 'user_nonce', 'user2_token', 'user2_nonce']
    for i in range(2):
        header['X-Auth-Token'] = test_parameter[auth[i * 2]]
        header['X-Auth-Nonce'] = test_parameter[auth[i * 2 + 1]]  
        urlName = '/api/v2/identity/track'
        body = {"liveMasterId": idList[0]}
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    api.blockUser(test_parameter['prefix'], test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], idList[4])

@pytest.fixture(scope='class')
def initForEdit():
    initdata.clearAnnouncement(test_parameter['db'])
    initdata.clearFansInfo(test_parameter['db'])
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']  
    urlName = '/api/v2/identity/track'
    body = {"liveMasterId": idList[0]}
    api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    body = {'title': 'test edit', 'content': '原始資訊', 'userLevel': ['bronze', 'silver']} 
    apiName = '/api/v2/liveMaster/announcement'
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)

def getTestData(funName):
    testData = []
    content = '內容恰為500  -'
    for i in range(480):
        content += str(0 * i)     
    if funName == 'create':
        #scenario, token, nonce, title, content, userLevel, isReset, expected
        testData = [
            ('標題長度超過20不能發送消息', 'broadcaster_token', 'broadcaster_nonce', '標題長度超過20不能發送消息1234567', content, ['bronze', 'silver'], False, 406),
            ('內容長度超過500不能發送消息', 'broadcaster_token', 'broadcaster_nonce', '內容長度超過500不能發送消息', content + '超過500個字囉。。。', ['bronze', 'silver'], False, 406),
            ('非直播主不能發送消息(只能用user來驗，因為admin也可發送訊息)', 'user_token', 'user_nonce', 'title 🤬長度恰好20個字可發送！＠', content, ['bronze', 'silver'], False, 401),
            ('當月首次發送應成功,titile及content恰為這20及500且只會發送給自己的粉絲', 'broadcaster_token', 'broadcaster_nonce', 'title 🤬長度恰好20個字可發送！＠', content, ['bronze', 'silver', 'diamond'], False, 200),
            ('當月已發送1次即不可再發送', 'broadcaster_token', 'broadcaster_nonce', '再次發送訊息', content, ['bronze', 'silver'], False, 406),
            ('每月1號0點即重置發送次數', 'broadcaster_token', 'broadcaster_nonce', '發送時間已重置', content, ['bronze', 'silver'], True, 200)
        ]
    elif funName == 'edit':
        #scenario, token, nonce, key, values, id, expected
        testData = [
            ('直播主編輯自己的消息title', 'broadcaster_token', 'broadcaster_nonce', 'title', '修改title', 1, 200),
            ('直播主編輯自己的消息內容', 'broadcaster_token', 'broadcaster_nonce', 'content', '修改內容', 1, 200),
            ('直播主編輯的消息不存在', 'broadcaster_token', 'broadcaster_nonce', 'content', '修改內容', 2, 404),
            ('直播主編輯自己的消息內容，但內容過長', 'broadcaster_token', 'broadcaster_nonce', 'content', content + '超過500個字囉。。。', 1, 406),
            ('直播主編輯自己的消息title，但title過長', 'broadcaster_token', 'broadcaster_nonce', 'title', '標題長度超過20不能修改消息1234567', 1, 406),    
            ('直播主編輯非自己的消息title', 'broadcaster1_token', 'broadcaster1_nonce', 'content', '修改內容', 1, 404)
        ]
    return testData

class TestAnnouncement():
    oriBody =  {'title': 'test edit', 'content': '原始資訊', 'userLevel': ['bronze', 'silver']} 
    def checkReciver(self, title, content, userLevel):
        time.sleep(30)
        levelDic = {
            'bronze':{'token': 'user1_token', 'nonce': 'user1_nonce', 'isReceiver': False, 'id': 3},
            'silver':{'token': 'user_token', 'nonce': 'user_nonce', 'isReceiver': True, 'id': 2},
            'diamond':{'token': 'user2_token', 'nonce': 'user2_nonce', 'isReceiver': False, 'id': 4}
        }
        for i in userLevel:
            header['X-Auth-Nonce'] = test_parameter[levelDic[i]['nonce']]
            header['X-Auth-Token'] = test_parameter[levelDic[i]['token']]
            apiName = '/api/v2/identity/' + idList[levelDic[i]['id']] + '/announcement/list?item=10&page=1'
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
            restext = json.loads(res.text)
            if levelDic[i]['isReceiver']:                
                assert restext['data']
                assert restext['data'][0]['title'] == title
                assert restext['data'][0]['content'] == content
            else:
                assert not restext['data']

    @pytest.mark.parametrize('scenario, token, nonce, title, content, userLevel, isReset, expected', getTestData('create'))
    def testCreateAnnounce(self,initForCreate, scenario, token, nonce, title, content, userLevel, isReset, expected):
        body = {'title': title, 'content': content, 'userLevel': userLevel}
        if isReset:
            date = (datetime.today()-timedelta(days=datetime.today().day)).strftime("%Y-%m-%d 15:59:59")
            sqlStr = "update announcement_v2 set create_at = '" + date + "', update_at = '" + date + "'"
            dbConnect.dbSetting(test_parameter['db'], [sqlStr])
        apiName = '/api/v2/liveMaster/announcement'
        header['X-Auth-Nonce'] = test_parameter[nonce]
        header['X-Auth-Token'] = test_parameter[token]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code == expected
        self.checkReciver(title, content, userLevel) if expected == 200 else None

    @pytest.mark.parametrize('scenario, token, nonce, key, values, id, expected', getTestData('edit'))
    def testEditAnnounce(self, initForEdit, scenario, token, nonce, key, values, id, expected):
        body =  {'title': None, 'content': None, 'userLevel': ['bronze', 'silver']} 
        body[key] = values
        keys = body.keys()
        for i in keys:
            body[i] = self.oriBody[i] if not body[i] else values
        pprint(body)
        apiName = '/api/v2/liveMaster/announcement/' + str(id)
        header['X-Auth-Nonce'] = test_parameter[nonce]
        header['X-Auth-Token'] = test_parameter[token]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code == expected
        if expected == 200:
            self.oriBody[key] = values
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
            restext = json.loads(res.text)
            restext['data']['id'] == id
            for i in keys:
                restext['data'][i] == body[i]
