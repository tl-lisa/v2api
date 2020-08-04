#milestone14 查詢他人個人資訊
#milestone22 若無頭像及暱稱則使用預設值
#hotfix userInfo加入cache 30秒，若是直播主或是使用者更新myinfo即需等30秒後才能取得新的資訊
#milestone23 新增user level
import json
import requests
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
idList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}


def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append('3420dkajfpi4wujfasdkdp')   
    header['X-Auth-Token'] = test_parameter['liveController1_token']
    header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
    url = '/api/v2/identity/myInfo'
    body = {'nickname': '231QQ', 'sex': 0, 'isPublicSexInfo': True, 'description': '我是liveController！！！', 'birthday': int(time.time() - 5000)}
    api.apiFunction(test_parameter['prefix'], header, url, 'put', body)
    time.sleep(30)
    
def teardown_module():
    pass


#scenario, token, nonce, idIndex, role, isUpdate, expect
testData = [
    ('user query', 'user_token', 'user_nonce', 2, 'ROLE_USER', False, 2),
    ('backend user query', 'backend_token', 'backend_nonce', 0, 'ROLE_MASTER', False, 2),
    ('boradcaster query', 'broadcaster_token', 'broadcaster_nonce', 1, 'ROLE_BUSINESS_MANAGER', False, 2),
    ('cs query', 'liveController1_token', 'liveController1_nonce', 3, 'ROLE_LIVE_CONTROLLER', True, 2),
    ('uuid is wrong', 'user_token', 'user_nonce', 4, '', False, 4),
    ('token/ nonce is wrong', 'err_token', 'err_nonce', 2, '', False, 4)
]

def checkCache(header, apiName, restext, body):
    time.sleep(10)
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    restext1 = json.loads(res.text)
    assert restext['data']['roles'][0]['name'] == restext1['data']['roles'][0]['name']
    assert restext['data']['profilePicture'] == restext1['data']['profilePicture']
    assert restext['data']['nickname'] == restext1['data']['nickname']
    assert restext['data']['selfDesc'] == restext1['data']['description']
    assert restext['data']['sexValue'] == restext1['data']['sex']
    time.sleep(20)
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    restext1 = json.loads(res.text)
    assert restext['data']['roles'][0]['name'] == restext1['data']['roles'][0]['name']
    assert restext['data']['profilePicture'] == restext1['data']['profilePicture']
    assert restext['data']['nickname'] == body['nickname']
    assert restext['data']['selfDesc'] == body['description']
    assert restext['data']['sexValue'] == body['sex']

@pytest.mark.parametrize("scenario, token, nonce, idIndex, role, isUpdate, expect", testData)
def testGetUserInfo(scenario, token, nonce, idIndex, role, isUpdate, expect):
    apiName = '/api/v2/identity/userInfo/'
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]   
    #print(apiName + idList[idIndex])
    res = api.apiFunction(test_parameter['prefix'], header, apiName + idList[idIndex], 'get', None)
    assert res.status_code // 100 == expect
    if expect == 2:
        restext = json.loads(res.text)
        assert restext['data']['roles'][0]['name'] == role
        assert len(restext['data']['profilePicture']) > 0
        assert len(restext['data']['nickname']) > 0
        assert len(restext['data']['userLevel']['levelId']) > 0
        assert restext['data']['userLevel']['levelNum'] >= 0
        if isUpdate:
            url = '/api/v2/identity/myInfo'
            body = {'nickname': '466123QQ', 'sex': 1, 'isPublicSexInfo': True, 'description': 'haha', 'birthday': int(time.time() - 5000)}
            api.apiFunction(test_parameter['prefix'], header, url, 'put', body)
            checkCache(header, apiName + idList[idIndex], restext, body)