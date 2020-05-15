#mileston19#869修改使用者role;若是轉成直播主，且level在白銀99以下，則應主動加上新秀的tage(tag_group=3; tag_id = 6)
import json
import requests
import pymysql
import time
import pytest
import string
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint

env = 'QA'
idList = []
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    idList.append(api.search_user(test_parameter['prefix'], 'track0041', header))
    idList.append(api.search_user(test_parameter['prefix'], 'track0042', header))

def teardown_module():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    url = '/api/v2/backend/user/role'
    body = {'ids': idList, 'role': 5}
    api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)

def getTestData():
    #token, nonce, idInfo, role, experience, expected
    testData = [
        ('backend_token', 'backend_nonce', idList, 4, 4577454, 2),
        ('backend_token', 'backend_nonce', idList, 5, 4577454, 2),
        ('backend_token', 'backend_nonce', idList, 1, 4577454, 2),
        ('backend_token', 'backend_nonce', idList, 10, 4577454, 2),
        ('liveController1_token', 'liveController1_nonce', idList, 4, 4577455, 2),
        ('broadcaster_token', 'broadcaster_nonce', idList, 5, 4577455, 4),
        ('err_token', 'err_nonce', idList, 5, 4577455, 4),
        ('backend_token', 'backend_nonce', '774ab73f-6aa6-4ed1-a991-609d7db7d1a3', 5, 4577455, 4)
    ]
    return testData

'''
・一般user（5）轉直播主（4）
・直播主轉一般user
・一般user轉admin（1）
・轉官方場控（10）
・非一般user 轉直播主,且經驗值超過白銀99（1502182）
・token/nonce無權限
・錯誤的token/nonce
'''
class TestChangeRole():
    @pytest.mark.parametrize("token, nonce, idInfo, role, experience, expected", getTestData())
    def test_changeRole(self,token, nonce, idInfo, role, experience, expected):
        ori_experience = 0
        if ori_experience != experience:
            sqlList = ["update user_experience set experience = " + str(experience) + " where identity_id = '" + idInfo[0] + "'"]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
            ori_experience = experience
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        url = '/api/v2/backend/user/role'
        body = {'ids': idInfo, 'role': role}
        res = api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)
        if type(idInfo) == list:
            id = idInfo[0] 
        else:
            id = idInfo
        sqlStr = "select count(*) from identity_tag_association where identity_id = '" + id + "' and tag_id = 6"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        print('dbcount=%d'%result[0][0])
        assert res.status_code // 100 == expected
        if role  == 4 and experience < 4577455:
            assert result[0][0] == 1
        else:
            assert result[0][0] == 0
