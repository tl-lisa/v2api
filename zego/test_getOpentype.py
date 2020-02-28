#mileston17 /api/v2/liveMaster/liveRoom/type
import time
import json
import pytest
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}


def init():
    initdata.set_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])
    sqlList = ["insert into zego_master values('" + idlist[0] + "')"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)

init()

def createTestdata():
    testData = [
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], [2, 1]),
        ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce']], [2, 0]),
        #([test_parameter['user_token'], test_parameter['user_nonce']], [4, 1]), 不做權限判斷，任何合法帳號皆可call
        ([test_parameter['err_token'], test_parameter['err_nonce']], [4, 1])
    ]
    return(testData)

@pytest.mark.parametrize("test_input, expected", createTestdata())
def testGetOpenType(test_input, expected):
    header['X-Auth-Token'] = test_input[0]
    header['X-Auth-Nonce'] = test_input[1]  
    apiName = '/api/v2/liveMaster/liveRoom/type'
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    #print(res.text)
    restext = json.loads(res.text)
    assert res.status_code // 100 == expected[0]
    if expected[0] == 2:
        assert restext['data']['type'] == expected[1]

