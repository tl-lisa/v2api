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
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    url = '/api/v2/backend/user/role'
    body = {'ids': [idList[0]], 'role': 4}
    api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)

#scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked, onairCount
#任何人皆可get直播主資訊
#黑名單不會影響到粉絲追蹤數
#直播主若未設置頭像要帶預設值
testData = [
    ('backend', 'backend_token', 'backend_nonce', 0, 1, False, False, False, False, 2, 0, False, 0),
    ('user tracking', 'user_token', 'user_nonce', 0, 1, True, False, False, False, 2, 1, True, 0),
    ('user blacking', 'user_token', 'user_nonce', 0, 1, False, True, False, False, 2, 1, True, 0),
    ('broadcaster', 'broadcaster_token', 'broadcaster_nonce', 0, 1, False, False, False, False, 2, 1, False, 0),
    ('without auth', 'err_token', 'err_nonce', 0, 1, False, False, False, False, 4, 1, True, 0),
    ('user1 and broadcaster onair', 'user1_token', 'user1_nonce', 0, 1, False, False, False, True, 2, 1, False, 0),
    ('user1 and broadcaster1 onair', 'user1_token', 'user1_nonce', 1, 0, False, False, False, False, 2, 0, False, 1),
    ('user1 and broadcaster transfer to user', 'user1_token', 'user1_nonce', 0, 1, False, False, True, False, 4, 1, False, 1)
]

@pytest.mark.parametrize("scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked, onairCount", testData)
def testMasterInfo(scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked, onairCount):
    chartInfo = []
    if isBlocking:
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId': idList[2]}
        api.add_block_user(test_parameter['prefix'], header, body)
    elif isChangeRole:
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
        url = '/api/v2/backend/user/role'
        body = {'ids': [idList[masterIndex]], 'role': 5}
        res = api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)
    elif isTracking:
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track'
        body = {"liveMasterId": idList[masterIndex]}
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    elif isOnAir:
        onAirTime = int(time.time()) 
        if onairCount == 0:
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
            apiName = '/api/v2/liveMaster/zego/liveRoom'
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {})
            restext = json.loads(res.text)
            chartInfo = sundry.Openroom(test_parameter['prefix'], header, 5, True, restext['data']['roomId'], 'Zego開播', 5)
        else:
            header['X-Auth-Token'] = test_parameter['broadcaster1_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce'] 
            chartInfo = sundry.Openroom(test_parameter['prefix'], header, 20, False, 0, '中華開播', 5)
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce] 
    urlName = '/api/v2/identity/masterInfo/' + idList[masterIndex]
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
    assert res.status_code // 100 == expected
    if expected == 2:
        restext = json.loads(res.text)
        pprint(restext)
        assert restext['data']['liveMasterId'] == idList[masterIndex]
        assert restext['data']['profilePicture'] is not None
        assert restext['data']['tracked'] == tracked
        assert restext['data']['fansCount'] == trackNum
        assert len(restext['data']['nickname']) > 0
        if isOnAir:
            assert restext['data']['roomCreateAt'] >= onAirTime 
            assert restext['data']['roomStatus'] == 1
            assert restext['data']['roomId'] == chartInfo[0]
            assert restext['data']['roomType'] == lineNum
            chartInfo[1].leave_room(chartInfo[0], chartInfo[2])  