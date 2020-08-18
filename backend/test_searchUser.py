#milestone28重測，因為效能調校，另外新加case #1326
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
checkItems = True
checkPages = True

def setup_module():
    initdata.set_test_data(env, test_parameter)

#scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, expected
testData = [
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'all', [1], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'all', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '1234', '', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '', '', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '', '', [1], '', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'nick_name', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [1,0,-1,-2], 'ROLE_ADMIN', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [1,0,-1,-2], 'ROLE_MASTER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [1,0,-1,-2], 'ROLE_LIVE_CONTROLLER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [1,0,-1,-2], 'ROLE_BUSINESS_MANAGER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [-2], 'ROLE_MASTER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'truelovelive', 'email', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'K76DN9E7', 'true_love_id', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'login_id', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'uuid', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'phone_number', [1,0,-1,-2], 'ROLE_USER', 2),
    ('wrond auth', 'user_token', 'user_nonce', '1234', 'all', [1], 'ROLE_USER', 4)
]

@pytest.mark.parametrize('scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, expected', testData)
def testSerchUser(scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, expected):
    global checkItems
    global checkPages
    body = {}
    body['keyword'] = keyword
    body['type'] = typeKind
    body['statusFilter'] = statusFilter
    body['roleFilter'] = roleFilter
    #print(body)
    header['X-Auth-Nonce'] = test_parameter[nonce]
    header['X-Auth-Token'] = test_parameter[token]
    apiName = '/api/v2/backend/user/search?item=20&page=1'
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    assert res.status_code // 100 == expected
    if expected == 2:
        restext = json.loads(res.text)
        assert restext['Status'] == 'Ok'
        assert restext['Message'] == 'SUCCESS'
        assert len(restext['data']) <= 20
        if all([len(restext['data']) > 5, checkItems]):
            checkItems = False
            apiName = '/api/v2/backend/user/search?item=3&page=1'
            res1 = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            restext1 = json.loads(res1.text)
            assert restext['data'] != restext1['data']
            assert len(restext1['data']) == 3
            assert restext['totalCount'] == restext1['totalCount']
        if all([restext['totalCount'] - 20 < 20, checkPages]):
            checkPages = False
            apiName = '/api/v2/backend/user/search?item=20&page=2'
            res1 = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            restext1 = json.loads(res1.text)
            assert restext['data'] != restext1['data']
            assert len(restext1['data']) < 20
            assert restext['totalCount'] == restext1['totalCount']