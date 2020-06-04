#milestone22 /api/v2/backend/chatBotSetting 限定LIVE_CONTROLLER才可以操作
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []


def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'], 
    test_parameter['broadcaster1_acc'], 'broadcaster050', 'broadcaster055', test_parameter['backend_acc']], idList)

testData = [
    ('only add auto chatBot', 'liveController1_token', 'liveController1_nonce', True, False, [], 2),
    ('add rush chatBot', 'liveController1_token', 'liveController1_nonce', False, True, [[0, 30, 'broadcaster005']], 2),
    ('add rush chatBot', 'liveController1_token', 'liveController1_nonce', False, True, [[2, 30, 'broadcaster050'], [3, 100, 'broadcaster055']], 2),
    ('add auto and rush chatBot', 'backend_token', 'backend_nonce', True, True, [[0, 30, 'broadcaster005'], [1, 60, 'broadcaster006'], [3, 60, 'broadcaster055']], 2),
    ('wrong auth', 'user_token', 'user_nonce', True, False, [], 4),
    ('auto setting is wrong', 'liveController1_token', 'liveController1_nonce', None, False, [], 4),
    ('rush setting is wrong', 'liveController1_token', 'liveController1_nonce', False, None, [], 4),
    ('add rush chatBot but without target', 'liveController1_token', 'liveController1_nonce', True, True, [], 2),
    ('add rush chatBot but target does not livemaster', 'liveController1_token', 'liveController1_nonce', False, True, [[4, 30, 'tl-lisa']], 4)
]

class TestEditBot():
    def setup_class(self):
        initdata.clearChatBot(test_parameter['db'])

    @pytest.mark.parametrize("scenario, token, nonce, isAuto, isRush, targetList, expected", testData)
    def testEdit(self, scenario, token, nonce, isAuto, isRush, targetList, expected):
        apiName = '/api/v2/backend/chatBotSetting'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        body = {}
        target = []
        body['autoChatBotSwitch'] = isAuto
        body['rushChatBotSwitch'] = isRush
        for i in targetList:
            pprint(i)
            targetBody = {}
            startTime = int(time.time())
            endTime = int(time.time()) + 300
            targetBody['id'] = idList[i[0]]
            targetBody['quantity'] = i[1]
            targetBody['startTime'] = startTime
            targetBody['endTime'] = endTime
            target.append(targetBody)
            time.sleep(1)
        body['rushChatBotTarget'] = target
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert res.status_code // 100 == expected
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        if token not in('liveController1_token', 'backend_token'):
            assert res.status_code // 100 == 4
        else:
            assert res.status_code // 100 == 2
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok'
            assert restext['Message'] == 'SUCCESS'
            assert restext['totalCount'] == len(targetList)
            assert restext['data']['autoChatBotSwitch'] == isAuto
            assert restext['data']['rushChatBotSwitch'] == isRush
            for i in restext['data']['rushChatBotTarget']:
                find = False
                for j in target:
                    if i['id'] == j['id']:
                        find = True
                        assert i['quantity'] == j['quantity']
                        assert i['startTime'] == j['startTime']
                        assert i['endTime'] == j['endTime']
                        assert i['nickname'] != ''
                assert find == True


