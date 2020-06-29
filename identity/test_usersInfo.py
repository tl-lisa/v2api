# Milestone 23.[New v2 API] 取得多名使用者公開資訊：POST /v2/identity/usersInfo/ #1282
import json
import requests
import pytest
from assistence import api
from assistence import initdata
from pprint import pprint
from assistence import dbConnect

env = 'QA2'
test_parameter = {}
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList=[]

def setup_module():
    initdata.set_test_data(env, test_parameter)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    header['Content-Type'] = 'application/json'
    #generate 46 accounts id and add in indList list
    account_list =[ "track{0:04d}".format(i) for i in range(101,147) ]
    global idList
    idList = [ api.search_user(test_parameter['prefix'], account, header) for account in account_list ]

    #generate 4 roles id and add in indList list
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'] ,
                       [test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'],
                       test_parameter['user1_acc']], idList)
#scenario, token, nonce, expect, result_num
test_data = [
    (       'user query 50',            'user_token',            'user_nonce', 2, 50),
    (    'backend query 50',         'backend_token',         'backend_nonce', 2, 50),
    ('boradcaster query 50',      'broadcaster_token',    'broadcaster_nonce', 2, 50),
    (         'cs query 50', 'liveController1_token', 'liveController1_nonce', 2, 50),
    (   'one uuid is wrong',            'user_token',            'user_nonce', 2, 50),
    ('user query result 51',            'user_token',            'user_nonce', 4, ''),
    (  'token/ nonce wrong',             'err_token',             'err_nonce', 4, ''),
]

@pytest.mark.parametrize("scenario, token, nonce, expect, result_num", test_data)
def test_users_info(scenario, token, nonce, expect, result_num):
    api_name = '/api/v2/identity/usersInfo/'
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]
    header['Content-Type'] = 'application/json'

    if scenario == 'one uuid is wrong':
        del idList[-1]
        idList.append('f32ed97a-657f-4e69-bee8-00000000000')
    elif scenario == 'user query result 51':
        idList.append('f32ed97a-657f-4e69-bee8-00000000001')
    data={
        "ids":[id for id in idList]
    }
    res = api.apiFunction(test_parameter['prefix'], header, api_name , 'post', data)
    assert res.status_code // 100 == expect
    restext = json.loads(res.text)
    if expect == 2:
        if scenario == 'one uuid is wrong':
            assert restext['data'][idList[-1]] == None
            assert len(restext['data']) == result_num
        else:
            assert restext['data'][idList[-1]]['roles'][0]['name'] == 'ROLE_USER'
            assert len(restext['data']) == result_num
    elif expect == 4:
        if scenario == 'user query result 51':
            assert restext['Message'] == '查詢數量超過上限'
        elif scenario == 'token/ nonce wrong':
            assert restext['Message'] == '使用者驗證錯誤，請重新登入'
