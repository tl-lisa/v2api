#milestone28重測，因為效能調校，另外新加case #1326
#milestone30 #1949 trueloveid在test做hash #1884回傳資料加入agencyName(經紀公司名稱)
import json
import requests
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint     import pprint
from datetime   import datetime,timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
checkItems = True
checkPages = True
trueLoveId = {}

#scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, coditionStr, items, expected
testData = [
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'all', [1], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'all', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '1234', '', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '', '', [0], 'ROLE_USER', 2),
    ('auth=admin;type is empty', 'backend_token', 'backend_nonce', '', '', [1], '', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'nick_name', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'login_id', [1,0,-1,-2], 'ROLE_ADMIN', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'broadcaster005', 'login_id', [1,0,-1,-2], 'ROLE_MASTER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'lv000', 'login_id', [1,0,-1,-2], 'ROLE_LIVE_CONTROLLER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'tl-lisa', 'login_id', [1,0,-1,-2], 'ROLE_BUSINESS_MANAGER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1', 'login_id', [-2], 'ROLE_MASTER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'truelovelive', 'email', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', 'track0050', 'true_love_id', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'login_id', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'uuid', [1,0,-1,-2], 'ROLE_USER', 2),
    ('auth=admin;input all condition', 'backend_token', 'backend_nonce', '1234', 'phone_number', [1,0,-1,-2], 'ROLE_USER', 2),
    ('wrond auth', 'user_token', 'user_nonce', '1234', 'all', [1], 'ROLE_USER', 4)
]

def addTrueloveId():
    sqlStr  = "select login_id, truelove_id from identity "
    sqlStr += "where login_id in ('tl-lisa', 'broadcaster005', 'track0050', 'lv000')"
    dbRes = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    for i in dbRes:
        trueLoveId[i[0]] = initdata.getTrueLoveId(i[1])

def addAgencyName():
    sqlStr = "delete from agency_master_contract"
    midDate1 = (datetime.today() - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    midDate = (datetime.today() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S')
    cDate = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr1  = "insert into agency_master_contract(create_at, contract_end_date, contract_start_date, master_charge_rate, agency_id, identity_id, version) values "
    sqlStr1 += "('" + cDate + "', '" + midDate + "', '2017-10-01 00:00:00', 0.3, 1, 'd82a7ba2-5c11-4615-aba7-2a768d927165', 1), "
    sqlStr1 += "('" + cDate + "',  '2028-10-01 00:00:00', '" + midDate1 + "', 0.3, 2, 'd82a7ba2-5c11-4615-aba7-2a768d927165', 2)"
    dbConnect.dbSetting(test_parameter['db'], [sqlStr, sqlStr1])

def setup_module():
    initdata.set_test_data(env, test_parameter)
    addTrueloveId()

@pytest.mark.parametrize('scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, expected', testData)
def testSerchUser(scenario, token, nonce, keyword, typeKind, statusFilter, roleFilter, expected):
    keywordDic = {'nick_name': 'nickname', 'email': 'email', 'true_love_id': 'trueLoveId', 'login_id': 'loginId', 'uuid': 'id', 'phone_number': 'verifiedPhone'}
    global checkItems
    global checkPages
    body = {}
    body['keyword'] = trueLoveId[keyword] if typeKind == 'true_love_id' else keyword
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
        for i in restext['data']:
            if i['loginId'] == 'broadcaster005':
                assert i['agencyName'] == '天使直播2'
            else:
                assert len(i['agencyName']) >= 0
            if all([typeKind != 'all', typeKind != 'true_love_id', typeKind != '', keyword != '']):
                assert keyword in i[keywordDic[typeKind]] 
            assert i['status'] in statusFilter
            if roleFilter:
                assert i['roles'][0]['name'] == roleFilter
            if i['loginId'] == keyword:
                assert i['trueLoveId'] == trueLoveId[keyword]
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