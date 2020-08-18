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
original = {}
idList = []

def initVerifyData():
    body = {}
    apiName = '/api/v2/backend/user/'
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    #可編輯 認證狀態 暱稱 真實名稱 性別 手機 個人簡介
    body['identityStatus'] = 1
    body['phoneNumber'] = '0988888888'
    body['selfDesc'] = '哇哈哈，超讚煮播'
    body['nickname'] = '123321'
    body['sex'] = 0
    body['realName'] = '竹本呆'
    original['account'] = {
        'accountNo': '',
        'bankName': '',
        'branchBank': '',
        'branchNo': ''
    }
    original['agencyId'] = ''
    original['agencyName'] = ''
    original['contractEndDate'] = None
    original['contractStartDate'] = None
    original['identityStatus'] = 1
    original['phoneNumber'] = '0988888888'
    original['selfDesc'] = '哇哈哈，超讚煮播'
    original['nickname'] = '123321'
    original['sexValue'] = 0
    original['realName'] = '竹本呆'
    original['loginId'] = 'liveAcc0004'
    original['trueLoveId'] = 'K76DN9E7'
    original['email'] = '123@gmail.com'
    original['3rdPartySource'] = ''
    original['fansCount'] = 1
    original['remainPoints'] = 0
    original['id'] = idList[4]
    original['userLevel'] = {
        "levelId": "bronze",
        "levelNum": 1
    }
    api.apiFunction(test_parameter['prefix'], header, apiName + idList[4], 'post', body)

def liveAcc0004Login():
    body = {
            "account":"liveAcc0004",
            "password":"123456",
            "pushToken":"tllisa123jhjayegrkldfkhgdkfasd"
        }
    res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json', 'Connection': 'Keep-alive'}, 
        '/api/v2/identity/auth/login', 'post', body)
    return res

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearFansInfo(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'],
    test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc'], 'liveAcc0004'], idList)
    header['X-Auth-Nonce'] = test_parameter['user_nonce']
    header['X-Auth-Token'] = test_parameter['user_token']
    api.set_tracking(test_parameter['prefix'], header, 'post', idList[4])
    res = liveAcc0004Login()
    restext = json.loads(res.text)
    header['X-Auth-Nonce'] = restext['data']['nonce']
    header['X-Auth-Token'] = restext['data']['token']
    api.set_tracking(test_parameter['prefix'], header, 'post', idList[0])
    initVerifyData()

def teardown_module():
    initVerifyData()

@pytest.fixture(scope="function")
def resetData():
    initVerifyData()

def getTestData(testType):
    testData = []
    if testType == 'update':
        #scenario, token, nonce, idIndex, fieldName, value, expect
        testData = [
            ('edit nickname', 'backend_token', 'backend_nonce', 4, 'nickname', '我 是 小 🤶🥰', 2),
            ('nickname is blank', 'backend_token', 'backend_nonce', 4, 'nickname', '     ', 2),
            ('edit selfDesc', 'backend_token', 'backend_nonce', 4, 'selfDesc', '🥰🥰🥰🥰....呼呼呼。。。。', 2),
            ('edit phone number', 'backend_token', 'backend_nonce', 4, 'phoneNumber', '22534239', 2),
            ('edit sexvalue', 'backend_token', 'backend_nonce', 4, 'sex', 1, 2),
            ('suspend account', 'backend_token', 'backend_nonce', 4, 'identityStatus', -2, 2),
            ('userid not found', 'backend_token', 'backend_nonce', -1, 'sex', 0, 4),
            ('without rights', 'user_token', 'user_nonce', 4, 'phoneNumber', '223344565', 4)
        ]
    return testData

class TestUserInfo():
    def compareData(self, apiName):
        checkList = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        checkList = original.keys()
        for i in checkList:
            assert restext[i] == original[i]
        
    def checkSuspend(self):
        res = liveAcc0004Login()
        restext = json.loads(res.text)
        assert restext['Message'] == 'ACCOUNT_HAS_BEEN_DISABLED'
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        res = api.get_fans_list(test_parameter['prefix'], header, idList[1] , '10', '1')
        assert str(res).find('liveAcc0004') == -1
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        apiName1 = '/api/v2/identity/track/liveMaster?item=999&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'get', None)
        assert str(res).find('liveAcc0004') == -1        

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, fieldName, value, expect', getTestData('update'))
    def testEditUserInfo(self, resetData, scenario, token, nonce, idIndex, fieldName, value, expect):
        body = {}
        apiName = '/api/v2/backend/user/'
        header['X-Auth-Nonce'] = test_parameter[nonce]
        header['X-Auth-Token'] = test_parameter[token]
        if idIndex >= 0:
            apiName += idList[idIndex]
        else:
            apiName += '23048iAgadsofu'
        body[fieldName] = value
        if all([len(str(value)) > 0, fieldName != 'sex']):
            original[fieldName] = value            
        elif fieldName == 'sex':
            original['sexValue'] = value
        if fieldName == 'identityStatus' and value == -2:
            original['fansCount'] = 0 
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expect
        if expect == 2:
            self.compareData(apiName)
            self.checkSuspend() if fieldName == 'identityStatus' else None
                