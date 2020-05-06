#milestone21 取得直播主資訊 #840
import json
import requests
import pymysql
import pytest
import time
import string
from datetime import datetime, timedelta
from ..assistence import dbConnect
from ..assistence import initdata
from ..assistence import api
from ..assistence import sundry
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
    sqlList = ["inster into zego_master values ('" + idList[0] + "')" ]
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    api.change_roles(test_parameter['prefix'], header, idList[0], 4)

#scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked
#任何人皆可get直播主資訊
#黑名單不會影響到粉絲追蹤數
#直播主若未設置頭像要帶預設值
testData = [
    ('backend', 'backend_token', 'backend_nonce', 0, 1, False, False, False, False, 2, 0, False),
    ('user tracking', 'user_token', 'user_nonce', 0, 1, True, False, False, False, 2, 1, True),
    ('user blacking', 'user_token', 'user_nonce', 0, 1, False, True, False, False, 2, 1, True),
    ('broadcaster', 'broadcaster_token', 'broadcaster_nonce', 0, 1, False, False, False, False, 2, 1, False),
    ('without auth', 'err_token', 'err_nonce', 0, 1, False, False, False, False, 4, 1, True),
    ('user1 and broadcaster onair', 'user1_token', 'user1_nonce', 0, 1, False, False, False, True, 2, 1, False),
    ('user1 and broadcaster transfer to user', 'user1_token', 'user1_nonce', 0, 1, False, False, True, False, 4, 1, False)
]

@pytest.mark.parametrize("scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked", testData)
def testMasterInfo(scenario, token, nonce, masterIndex, lineNum, isTracking, isBlocking, isChangeRole, isOnAir, expected, trackNum, tracked):
    if isBlocking:
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId': idList[2]}
        api.add_block_user(test_parameter['prefix'], header, body)
    elif isChangeRole:
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
        api.change_roles(test_parameter['prefix'], header, idList[masterIndex], 5) 
    elif isTracking:
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track'
        body = {"liveMasterId": idList[masterIndex]}
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    elif isOnAir:
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        rid = sundry.Openroom(test_parameter['prefix'], header, 20, True, 0, 'test', 5)
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce] 
    urlName = '/api/v2/identity/masterInfo/' + idList[masterIndex]
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
    assert res.status_code // 100 == expected
    if expected == 2:
        restext = json.loads(res.text)
        assert restext['data']['liveMasterId'] == idList[masterIndex]
        assert restext['data']['proftilePicture'] is not None
        assert restext['data']['roomType'] == lineNum
        assert restext['data']['tracked'] == tracked
        assert restext['data']['fansCount'] == trackNum
        if isOnAir:
            onAirTime = time.time()
            assert restext['data']['roomCreateAt']['year'] == time.strftime("%Y", onAirTime) 
            assert restext['data']['roomCreateAt']['month'] == time.strftime("%m", onAirTime) 
            assert restext['data']['roomCreateAt']['minutes'] == time.strftime("%M", onAirTime) 
            assert restext['data']['roomCreateAt']['hours'] == time.strftime("%H", onAirTime) 
            assert restext['data']['roomCreateAt']['day'] == time.strftime("%d", onAirTime) 
            assert restext['data']['roomStatus'] == 1
            assert restext['data']['roomId'] == rid
    