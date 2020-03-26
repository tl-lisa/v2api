#milestone19 #858 Line login 用line順便驗證第3方登入的流程
import json
import requests
import pymysql
import pytest
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import lineLogin
from pprint import pprint

env = 'testing'
test_parameter = {}


def setup_module():
    initdata.set_test_data(env, test_parameter)
    sqlList = []
    tableList = ['identity_third_party', 'identity_line']
    sqlStr = 'select identity_id from identity_third_party'
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    for i in tableList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)       
    for i in range(len(result[0])):
        if i == 0:
            sqlStr = "delete from identity where id in ('"
        sqlStr += result[0][i] 
        if i == len(result[0]):
            sqlStr += "')"
        else:
            sqlStr += "', '"
    sqlList.append(sqlStr)
    sqlList.append("alter table " + tableList[0] + " auto_increment = 1") 
    dbConnect.dbSetting(test_parameter['db'], sqlList)


def getTestData():
    #condition, expected
    testData = [
        ('firstLogin', 2),
        ('secondLogin', 2),
        ('accToken_Wrong', 4),
        ('idToken_Wrong', 4),
        ('expired', 4)
    ]
    return testData

class TestLineLogin():
    auth = []
    '''
    ・第一次用line登入建立帳號，會導到email綁定頁面
    ・第二次用line登入，則不會導到email綁定頁面
    ・access token錯誤，登入失敗
    ・id token錯誤。登入失敗
    ・資訊皆正確，但access token expired，登入失敗
    '''
    @pytest.mark.parametrize("condition, expected", getTestData())
    def testlineFlow(self, condition, expected):
        url = '/api//v2/3rdParty/line/verify'
        if condition == 'firstLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.extend([idToken, accessToken])
        elif condition == 'secondLogin':
            idToken, accessToken = (lineLogin.line_login())
            body = {
                'accessToken': accessToken,
                'idToken': idToken
            }
            self.auth.extend([idToken, accessToken])
        elif condition == 'accToken_Wrong':
            body = {
                'accessToken': self.auth[0],
                'idToken': idToken[3]
            }
        elif condition == 'idToken_Wrong':
            body = {
                'accessToken': self.auth[2],
                'idToken': idToken[1]
            }
        elif condition == 'expired':
            body = {
                'accessToken': self.auth[0],
                'idToken': idToken[1]
            }
        res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
        assert res.status_code == expected
        if condition == 'firstLogin':
            restext = json.loads(res.text)
            assert restext['data']['isNew'] == 1
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
        if condition == 'secondLogin':
            assert restext['data']['isNew'] == 0
            assert 'nonce' in restext['data']
            assert 'token' in restext['data']
            assert 'idToken' in restext['data']
        