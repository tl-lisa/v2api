import json
import requests
import time
import string
import pytest
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
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

def teardown_module():
    pass


#scenario, token, nonce, idIndex, role, expect
testData = [
    ('user query', 'user_token', 'user_nonce', 2, 'ROLE_LIVE_CONTROLLER',2),
    ('backend user query', 'backend_token', 'backend_nonce', 0, 'ROLE_MASTER', 2),
    ('boradcaster query', 'brodcaster_token', 'broadcaster_nonce', 1, 'ROLE_BUSINESS_MANAGER', 2),
    ('cs query', 'liveController1_token', 'liveController1_nonce', 3, 'ROLE_USER', 2),
    ('uuid is wrong', 'user_token', 'user_nonce', 4, '', 4),
    ('token/ nonce is wrong', 'err_token', 'err_nonce', 2, '', 4)
]

@pytest.mark.parametrize("scenario, token, nonce, idIndex, role, expect", testData)
def testGetUserInfo(scenario, token, nonce, idIndex, role, expect):
    apiName = '/api/v2/identity/userInfo/'
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]   
    res = api.apiFunction(test_parameter['prefix'], header, apiName + idList[idIndex], 'get', None)
    assert res.status_code // 100 == expect
    if expect == 2:
        restext = json.loads(res.text)
        assert restext['data']['roles'][0]['name'] == role
        assert len(restext['data']['profilePicture']) > 0
