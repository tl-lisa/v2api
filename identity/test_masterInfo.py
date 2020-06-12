#milestone21 取得直播主資訊 #840
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


def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'], 
    test_parameter['broadcaster1_acc'], test_parameter['backend_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idList)
    initdata.clearFansInfo(test_parameter['db'])
    sqlList = ["insert into zego_master values ('" + idList[0] + "')" ]
    dbConnect.dbSetting(test_parameter['db'], sqlList)

def teardown_module():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    url = '/api/v2/backend/user/role'
    body = {'ids': [idList[0]], 'role': 4}
    api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)

#scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked
#scenario, token, nonce, masterIndex, lineNum, ac, expected, trackNum, tracked, onairCount
#任何人皆可get直播主資訊
#黑名單不會影響到粉絲追蹤數
#直播主若未設置頭像要帶預設值

testData = [
    ('backend', 'backend_token', 'backend_nonce', 0, 1, '', 2, 0, False),
    ('user tracking', 'user_token', 'user_nonce', 0, 1, 'tracking', 2, 1, True),
    ('user blacking', 'user_token', 'user_nonce', 0, 1, 'block', 2, 1, True),
    ('broadcaster', 'broadcaster_token', 'broadcaster_nonce', 0, 1, '', 2, 1, False),
    ('without auth', 'err_token', 'err_nonce', 0, 1, '', 4, 1, True),
    ('user1 and broadcaster onair', 'user1_token', 'user1_nonce', 0, 1, 'onAir', 2, 1, False),
    ('user1 and broadcaster1 onair', 'user1_token', 'user1_nonce', 1, 0, '', 2, 0, False),
    ('user1 and broadcaster transfer to user', 'user1_token', 'user1_nonce', 0, 1, 'changeRole', 4, 1, False)
]

@pytest.mark.parametrize("scenario, token, nonce, masterIndex, lineNum, action, expected, trackNum, tracked", testData)
def testMasterInfo(scenario, token, nonce, masterIndex, lineNum, action, expected, trackNum, tracked):
    chartInfo = []
    actionDic = {
        'block': {'token': 'broadcaster_token', 'nonce': 'broadcaster_nonce', 'body': {'userId': idList[2]}, 'apiName': '/api/v2/liveMaster/blockUser', 'way': 'post'},
        'changeRole': {'token': 'backend_token', 'nonce': 'backend_nonce', 'body': {'ids': [idList[masterIndex]], 'role': 5}, 'apiName': '/api/v2/backend/user/role', 'way': 'patch' },
        'tracking': {'token': token, 'nonce': nonce, 'body': {"liveMasterId": idList[masterIndex]}, 'apiName': '/api/v2/identity/track', 'way': 'post' },
        'onAir': {'token': 'broadcaster_token', 'nonce': 'broadcaster_nonce', 'body': {}, 'apiName': '/api/v2/liveMaster/zego/liveRoom', 'way': 'post' }
    }
    if action != '':
        header['X-Auth-Token'] = test_parameter[actionDic[action]['token']]
        header['X-Auth-Nonce'] = test_parameter[actionDic[action]['nonce']]
        if action != 'onAir':
            api.apiFunction(test_parameter['prefix'], header, actionDic[action]['apiName'], actionDic[action]['way'], actionDic[action]['body'])
        else:
            onAirTime = int(time.time()) 
            res = api.apiFunction(test_parameter['prefix'], header, actionDic[action]['apiName'], actionDic[action]['way'], actionDic[action]['body'])
            restext = json.loads(res.text)
            chartInfo = sundry.Openroom(test_parameter['prefix'], header, 5, True, restext['data']['roomId'], 'Zego開播', 5)
    time.sleep(30)
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce] 
    urlName = '/api/v2/identity/masterInfo/' + idList[masterIndex]
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
    assert res.status_code // 100 == expected
    if expected == 2:
        restext = json.loads(res.text)
        pprint(restext)
        assert restext['data']['liveMasterId'] == idList[masterIndex]
        assert len(restext['data']['profilePicture']) > 0
        assert restext['data']['tracked'] == tracked
        assert restext['data']['fansCount'] == trackNum
        assert len(restext['data']['nickname']) > 0
        if action == 'onAir':
            assert restext['data']['roomCreateAt'] >= onAirTime 
            assert restext['data']['roomStatus'] == 1
            assert restext['data']['roomId'] == chartInfo[0]
            assert restext['data']['roomType'] == lineNum
            chartInfo[1].leave_room(chartInfo[0], chartInfo[2])  
