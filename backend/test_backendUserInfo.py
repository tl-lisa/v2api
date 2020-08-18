#milestone28加入get userInfo的測試案例 #1327
import json
import requests
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import lineLogin
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
    original['trueLoveId'] = 'GNMRWKD5'
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
    sqlStr  = "insert into identity_profile set identity_id = '0610edb2-2c38-4089-b664-c54d8e3ec0b4', "
    sqlStr += "email = '123@gmail.com', created_at = '2020-08-12 08:54:27', updated_at = '2020-08-12 08:54:27'"
    dbConnect.dbSetting(test_parameter['db'], [sqlStr])
    return res

def createAccountByEmail():
    head = {'Content-Type': 'application/json'}
    url = '/api/v2/identity/register/email/send'
    body = {
                'email': 'lisa@truelovelive.dev',
                'password': '12345',
                'pushToken': 'emailRegrjhjayegrkldfkhgdkfasd'
            }
    res = api.apiFunction(test_parameter['prefix'], head, url, 'post', body)  
    restext = json.loads(res.text)    
    tempToken = restext['data']['tmpToken']
    sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    actCode = result[0][0]
    url = '/api/v2/identity/register/email/activate'
    body = {
            "tmpToken": tempToken,
            "activateCode": actCode,
            "pushToken": "emailRegrjhjayegrkldfkhgdkfasd"
        }
    api.apiFunction(test_parameter['prefix'], head, url, 'post', body)
    sqlStr = "select id from identity where login_id = 'lisa@truelovelive.dev'" 
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    print('email註冊的uid(%s)'%result[0][0])
    return result[0][0]

def loginByLine():
    url = '/api/v2/3rdParty/line/verify'
    idToken, accessToken = (lineLogin.line_login())
    body = {
        'accessToken': accessToken,
        'idToken': idToken
    }
    api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
    sqlStr = "select identity_id from identity_third_party" 
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    return result[0][0]

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])
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
    idList.append(createAccountByEmail())
    idList.append(loginByLine())
    initVerifyData()

def teardown_module():
    initVerifyData()
    dbConnect.dbSetting(test_parameter['db'], ["delete from identity_profile where identity_id = '0610edb2-2c38-4089-b664-c54d8e3ec0b4'"])

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
    elif testType == 'get':
        #scenario, token, nonce, idIndex, compareKey, compareValue, roleType, expect
        testData = [
            ('查詢身份別為直播主', 'backend_token', 'backend_nonce', 4, '', '', 'ROLE_MASTER', 2),
            ('查詢原舊帳號為user', 'backend_token', 'backend_nonce', 2, '', '', 'ROLE_USER', 2),
            ('查詢email登入且為user', 'backend_token', 'backend_nonce', 5, 'email', 'lisa@truelovelive.dev', 'ROLE_USER', 2),
            ('查詢line登入且為user', 'backend_token', 'backend_nonce', 6, '3rdPartySource', 'Line', 'ROLE_USER', 2),
            ('一般user登入無權限', 'user_token', 'user_nonce', 4, '', '', 'ROLE_USER', 4)
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

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, compareKey, compareValue, roleType, expect', getTestData('get'))
    def testGetSingleUserInfo(self, scenario, token, nonce, idIndex, compareKey, compareValue, roleType, expect):
        apiName = '/api/v2/backend/user/' + idList[idIndex]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        header['X-Auth-Token'] = test_parameter[token]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == expect
        if expect == 2:
            restext = json.loads(res.text)
            #assert restext['roles'][0]['name'] == roleType
            assert len(restext['profilePicture']) > 0
            assert restext.get('trueLoveId')
            if compareKey != '':
                assert restext[compareKey] == compareValue
                assert restext['userLevel']['levelId'] == 'bronze'
                assert restext['userLevel']['levelNum'] == 1
        