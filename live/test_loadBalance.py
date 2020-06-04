#milestone22 #1160 直播主取得 socket IP & port資訊
import json
import requests
import time
import string
import pytest
from assistence import api
from assistence import initdata
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)


#僅驗證權限及回復資訊是否完整
testData = [
    ('broadcaster get info', 'broadcaster_token', 'broadcaster_nonce', 2),
    ('backend get info', 'backend_token', 'backend_nonce', 4),
    ('livecontroller get info', 'liveController1_token', 'liveController1_nonce', 4),
    ('user get info', 'user_token', 'user_nonce', 4),
    ('error auth', 'err_token', 'err_nonce', 4)
]

@pytest.mark.parametrize('scenario, token, nonce, expected', testData)   
def test_loadBalance(scenario, token, nonce, expected):
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]
    apiName = '/api/v2/liveMaster/loadBalance'
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    assert res.status_code // 100 == expected
    if expected == 2:
        restext = json.loads(res.text)
        assert restext['Status'] == 'Ok'
        assert restext['Message'] == 'SUCCESS'
        assert restext['data']['socketIp'] is not None
        assert restext['data']['socketPort'] is not None