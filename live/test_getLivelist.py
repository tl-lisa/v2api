#mileston17 /v2/livelist/liveRoom?tag=1&tagGroup=1&item=20&page=1; 未給tag視作全撈（hotlist);tag 的case後補
import json
import requests
import time
import string
import pytest
import socket
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import chatlib
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
zegoInfo = [0, 0]


def setup_module():
    sqlList = []
    create_At = int((datetime.today() - timedelta(hours=8)).strftime('%s'))
    initdata.set_test_data(env, test_parameter)    
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearLiveData(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [
    test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc']
    ], idlist )
    for i in range(2):
        sqlStr = "insert into zego_master values('" + idlist[i] + "')"
        sqlList.append(sqlStr)
    sqlStr = "insert into top_sort values('" + idlist[0] + "', FROM_UNIXTIME(" + str(create_At) 
    sqlStr += ", '%Y-%m-%d %H:%i:%s'), 'lisa', FROM_UNIXTIME(" + str(create_At) + ", '%Y-%m-%d %H:%i:%s'), 'lisa', 3, 0)" 
    sqlList.append(sqlStr)
    dbConnect.dbSetting(test_parameter['db'], sqlList)
 
def teardown_module():
    for i in range (1, (len(zegoInfo) // 2)):
        chatlib.leave_room(zegoInfo[i * 2], zegoInfo[i * 2  + 1])


def openZego(token, nonce):
    header1= {'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter[token], 'X-Auth-Nonce': test_parameter[nonce]}
    apiName = '/api/v2/liveMaster/zego/liveRoom'
    res = api.apiFunction(test_parameter['prefix'], header1, apiName, 'post', {})
    restext = json.loads(res.text)
    roomId = restext['data']['roomId']
    zegoInfo.append(roomId)
    sockinfo = api.get_load_balance(test_parameter['prefix'], header1)
    sip = sockinfo['socketIp']
    sport = int(sockinfo['socketPort'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    zegoInfo.append(sock)
    server_address = (sip, sport)
    sock.connect(server_address)
    chatlib.chat_room_auth(sock, header1)  
    chatlib.enterZego(sock, roomId)
    return

#scenario, token, nonce, condition, action, master_token, master_nonce, zegoInfoindex, totalCount, masterList, roomId, roomStatus, expected
testData = [
    ('one master on air, and user get list', 'user_token', 'user_nonce', 'item=5&page=1', 'open', 'broadcaster1_token', 'broadcaster1_nonce', 0, 1, [1], [1], [1], 2),
    ('two master on air, and user get list', 'user1_token', 'user1_nonce', 'item=5&page=1', 'open', 'broadcaster_token', 'broadcaster_nonce', 0, 2, [0, 1], [2,1], [1, 1], 2),
    ('query tagGroup = 5', 'user1_token', 'user1_nonce', 'tagGroup=5&item=5&page=1', '', 'broadcaster_token', 'broadcaster_nonce', 0, 1, [1], [1], [1], 2),
    ('one on air, the other close', 'user1_token', 'user1_nonce', 'item=5&page=1', 'close', 'broadcaster_token', 'broadcaster_nonce', 2, 2, [1, 0], [1, 2], [1, 0], 2),
    ('query by onAir', 'user1_token', 'user1_nonce', 'item=5&page=1&roomStatus=1', '', 'broadcaster_token', 'broadcaster_nonce',  0, 1, [1], [1], [1], 2),
    ('query tagGroup = 1', 'user1_token', 'user1_nonce', 'tagGroup=1&item=5&page=1', '', 'broadcaster1_token', 'broadcaster1_nonce',  0, 0, [], [], [], 2),
    ('wrong auth', 'err_token', 'err_nonce', 'tagGroup=5&item=5&page=1', '', 'broadcaster_token', 'broadcaster_nonce', 0, 1, [1], [1], [1], 4)
]

@pytest.mark.parametrize("scenario, token, nonce, condition, action, master_token, master_nonce, index, totalCount, masterList, roomId, roomStatus, expected", testData)
def testGetLiveList(scenario, token, nonce, condition, action, master_token, master_nonce, index, totalCount, masterList, roomId, roomStatus, expected):
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce] 
    actionDic = {'open': openZego, 'close': chatlib.leave_room}
    parameterDic = {'open': [master_token, master_nonce], 'close': [zegoInfo[index * 2], zegoInfo[index * 2 + 1]]}
    actionDic[action](parameterDic[action][0], parameterDic[action][1]) if action != '' else None
    time.sleep(5)
    apiName = '/api/v2/live/list/liveRoom?' + condition
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', {})
    restext = json.loads(res.text)
    assert res.status_code // 100 == expected
    if all([expected == 2, totalCount >0]):
        pprint(restext)
        assert 'description' in restext['data'][0]
        assert 'nickname' in restext['data'][0]  
        assert 'roomPoint' in restext['data'][0]       
        assert restext['totalCount'] == totalCount
        for i in range(totalCount):
            assert restext['data'][i]['liveMasterId'] == idlist[masterList[i]]
            assert restext['data'][i]['roomId'] ==  zegoInfo[roomId[i] * 2]
            assert restext['data'][i]['roomStatus'] == roomStatus[i]
            assert len(restext['data'][0]['profilePicture']) > 0