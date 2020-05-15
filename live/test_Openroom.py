#mileston17 /api/v2/liveMaster/zego/liveRoom
import time
import json
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
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
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], [2], False),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], [4], True),
        ([test_parameter['user_token'], test_parameter['user_nonce']], [4], False), 
        ([test_parameter['err_token'], test_parameter['err_nonce']], [4], False)

    ]
    return(testData)

@pytest.mark.parametrize("test_input, expected, isChangeRole", createTestdata())
def testGetOpenType(test_input, expected, isChangeRole):
    if isChangeRole:
        changelist = [idlist[0]] 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '5') #轉成一般用戶
    header['X-Auth-Token'] = test_input[0]
    header['X-Auth-Nonce'] = test_input[1]  
    apiName = '/api/v2/liveMaster/zego/liveRoom'
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {})
    restext = json.loads(res.text)
    pprint(restext)
    assert res.status_code // 100 == expected[0]
    if expected[0] == 2:
        rid = sundry.Openroom(test_parameter['prefix'], header, 5, True, restext['data']['roomId'], 'Zegp開播', 5)
        assert restext['data']['roomId'] == rid
        assert restext['data']['streamId'] > 0
    if isChangeRole:
        changelist = [idlist[0]] 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主

