#mileston17 /v2/livelist/liveRoom?tag=1&tagGroup=1&item=20&page=1; 未給tag視作全撈（hotlist);tag 的case後補
import json
import requests
import time
import string
import pytest
import socket
import multiprocessing as mp
import traceback
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
zegoInfo = []
chinaInfo = []


def init():
    create_At = int((datetime.today() - timedelta(hours=8)).strftime('%s'))
    initdata.set_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])
    sqlList = ["insert into zego_master values('" + idlist[0] + "')"]
    sqlStr = "insert into top_sort values('" + idlist[0] + "', FROM_UNIXTIME(" + str(create_At) + ", '%Y-%m-%d %H:%i:%s'), 'lisa', FROM_UNIXTIME(" + str(create_At) + ", '%Y-%m-%d %H:%i:%s'), 'lisa', 3, 0)" 
    sqlList.append(sqlStr)
    dbConnect.dbSetting(test_parameter['db'], sqlList)
 

def openZego():
    header1= {'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['broadcaster_token'], 'X-Auth-Nonce': test_parameter['broadcaster_nonce']}
    apiName = '/api/v2/liveMaster/zego/liveRoom'
    res = api.apiFunction(test_parameter['prefix'], header1, apiName, 'post', {})
    restext = json.loads(res.text)
    roomId = restext['data']['roomId']
    sockinfo = api.get_load_balance(test_parameter['prefix'], header1)
    sip = sockinfo['socketIp']
    sport = int(sockinfo['socketPort'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (sip, sport)
    sock.connect(server_address)
    chatlib.chat_room_auth(sock, header1)  
    chatlib.enterZego(sock, roomId)
    return(sock, roomId)


def openChina():
    header2= {'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['broadcaster1_token'], 'X-Auth-Nonce': test_parameter['broadcaster1_nonce']}
    sockinfo = api.get_load_balance(test_parameter['prefix'], header2)
    sip = sockinfo['socketIp']
    sport = int(sockinfo['socketPort'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (sip, sport)
    sock.connect(server_address)
    chatlib.chat_room_auth(sock, header2)  
    rid = chatlib.new_room(sock, 'China line')
    return(sock, rid)

init()
zegoInfo = openZego()
chinaInfo = openChina()

def teardown_module():
    chatlib.leave_room(zegoInfo[1], zegoInfo[0])
    chatlib.leave_room(chinaInfo[1], chinaInfo[0])

def createTestdata():
    print('creatTestdata')
    testData = [
        ([test_parameter['user_token'], test_parameter['user_nonce'], '', 10, 1, ''], [2, 2]),
        ([test_parameter['user_token'], test_parameter['user_nonce'], '', 10, 1, 'zego'], [2, 2]),
        ([test_parameter['user_token'], test_parameter['user_nonce'], '', 10, 1, 'china'], [2, 2]),
        ([test_parameter['user_token'], test_parameter['user_nonce'], '', 1, 1, ''], [2, 1]), 
        ([test_parameter['user_token'], test_parameter['user_nonce'], '', 1, 2, ''], [2, 1]), 
        ([test_parameter['err_token'], test_parameter['err_nonce'], '', 10 ,1, ''], [4, 0])
    ]
    return(testData)

@pytest.mark.parametrize("test_input, expected", createTestdata())
def testGetLiveList(test_input, expected):
    header['X-Auth-Token'] = test_input[0]
    header['X-Auth-Nonce'] = test_input[1] 
    if test_input[5] == 'zego':
        chatlib.leave_room(zegoInfo[1], zegoInfo[0])
        time.sleep(5)
    elif test_input[5] == 'china':
        chatlib.leave_room(chinaInfo[1], chinaInfo[0])
        time.sleep(5)
    if test_input[2] == '':
        apiName = '/api/v2/live/list/liveRoom?' + 'item=' + str(test_input[3]) + '&page=' + str(test_input[4])
    else:
        apiName = '/api/v2/live/list/liveRoom?' + test_input[2] + '&item=' + str(test_input[3]) + '&page=' + str(test_input[4])
    #print(apiName)
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', {})
    restext = json.loads(res.text)
    assert res.status_code // 100 == expected[0]
    if expected == 2:
        assert restext['data'][0].has_key('tags') == True
        assert restext['data'][0].has_key('videoUrl') == True
        assert restext['data'][0].has_key('description') == True
        if test_input[3] > 1:
            if test_input[5] != 'zego':
                assert restext['totalCount'] == expected[1]
                assert restext['data'][0]['liveMasterId'] == idlist[0]
                assert restext['data'][1]['liveMasterId'] == idlist[1] 
            else:
                assert restext['totalCount'] == expected[1]
                assert restext['data'][0]['liveMasterId'] == idlist[1]
                assert restext['data'][1]['liveMasterId'] == idlist[0]
        else:
            if test_input[3] == 1:
                assert restext['totalCount'] == expected[1]
                assert restext['data'][0]['liveMasterId'] == idlist[0]
            else:
                assert restext['totalCount'] == expected[1]
                assert restext['data'][0]['liveMasterId'] == idlist[1]


