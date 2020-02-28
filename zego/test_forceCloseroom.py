##mileston17 #767 /api/v2/backend/liveMaster/liveRoom/{room_id}; 未給tag視作全撈（hotlist);tag 的case後補
import json
import requests
import time
import string
import pytest
import socket
import multiprocessing as mp
import traceback
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import chatlib
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
zegoInfo = []


def init():
    initdata.set_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])
 

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


init()

def teardonw_functiob():
    chatlib.leave_room(zegoInfo[1], zegoInfo[0])
    time.sleep(5)

def createTestdata():
    print('creatTestdata')
    testData = [
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], False], [2]),
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], True], [2]),
        ([test_parameter['liveController1_token'], test_parameter['liveController1_nonce'], False], [2]),
        ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], False], [4]),
        ([test_parameter['user_token'], test_parameter['user_nonce'], False], [4]),
        ([test_parameter['err_token'], test_parameter['err_nonce'], False], [4])
    ]
    return(testData)


@pytest.mark.parametrize("test_input, expected", createTestdata())
def testGeLiveList(test_input, expected):
    zegoInfo = openZego()
    print('room id = %d' %zegoInfo[1])
    chatlib.leave_room(zegoInfo[1], zegoInfo[0]) if test_input[2] else None
    header['X-Auth-Token'] = test_input[0]
    header['X-Auth-Nonce'] = test_input[1] 
    apiName = '/api/v2/backend/liveMaster/liveRoom/' + str(zegoInfo[1])
    print(apiName)
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
    assert res.status_code // 100 == expected[0]
    time.sleep(3)