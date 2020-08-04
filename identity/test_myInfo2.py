#milestone19 V2取得，修改個人資訊 #863
#milestone21 #1125 第3方登入第1個字母大寫  #1005追加trueLove ID
#milestone23 #1272 如果有修改myinfo會自動清cache，且nickname不可為空字串 #userinfo cache 時間合併在myinfo中驗證
#milestone26 #1626 #1627 如果role= user or live_controller其暱稱需超過30天才可更改（首次註冊輸入的暱稱不計）
#milestone27 #
import json
import requests
import pymysql
import pytest
import time
import string
from datetime import datetime, timedelta
from assistence import dbConnect
from assistence import initdata
from assistence import api
from assistence import lineLogin
from pprint import pprint

env = 'QA'
test_parameter = {}
idList = []
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    dbConnect.dbSetting(test_parameter['db'], ["update identity set nickname = '123QQ' where login_Id in ('track0050', 'broadcaster005', 'lv000')"])
    initdata.clearIdentityData(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['user_acc'], test_parameter['user1_acc']], idList)

def regByMail():
    url = '/api/v2/identity/register/email/send'
    body = {
                'email': 'tl-lisa@truelovelive.dev',
                'password': '12345'
            }
    res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body)   
    restext = json.loads(res.text)     
    tempToken = restext['data']['tmpToken']
    sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    actCode = result[0][0]
    url = '/api/v2/identity/register/email/activate'
    body = {
            "tmpToken": tempToken,
            "activateCode": actCode,
            "pushToken": "dshfklkrxkeiyegrkldfkhgdkfasd"
        }
    res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body) 
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])    

def loginByLine():
    url = '/api/v2/3rdParty/line/verify'
    idToken, accessToken = (lineLogin.line_login())
    body = {
        'accessToken': accessToken,
        'idToken': idToken
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])    

def loginByAccount():
    url = '/api/v2/identity/auth/login'
    body = {
        "account": "track0005",
        "password": "123456",
        "pushToken":"dshfklkrjhjayegrkldfkhgdkfasd"
    }
    res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body) 
    restext = json.loads(res.text)
    return(restext['data']['token'], restext['data']['nonce'], restext['data']['idToken'])

def getData(testName):
    if testName == 'getInfo':
        #token, nonce, account, role, expected
        testData = [
            ('user_token', 'user_nonce', 'user_acc', 5, 2),
            ('user1_token', 'user1_nonce', 'user1_acc', 5, 2),
            ('broadcaster_token', 'broadcaster_nonce', 'broadcaster_acc', 4, 2),
            ('backend_token', 'backend_nonce', 'backend_acc', 7, 2),
            ('liveController1_token', 'liveController1_nonce', 'liveController1_acc', 10, 2),
            ('err_token', 'err_nonce', '', '', 4)
        ]
    if testName == 'updateInfo':
        #scenario, token, nonce, keyInfo, valueInfo, action, intervalDay, expected
        testData = [
            ('nickname不允許空值', 'user_token', 'user_nonce', 'nickname', '', None, '0', 4),
            ('nickname長度限制12，輸入13位應失敗', 'broadcaster_token', 'broadcaster_nonce', 'nickname', '1234567890123', None, '', 4),
            ('直播主更改自己的nickname應成功', 'broadcaster_token', 'broadcaster_nonce', 'nickname', '🥰🥰🥰 🥰❤️💞💝💝12', None, '', 2),
            ('直播主30天內更改自己的nickname應成功', 'broadcaster_token', 'broadcaster_nonce', 'nickname', '🥰🥰🥰 哇 ❤️💞💝❤️💞', None, '', 2),
            ('使用者首次更新自己的nickname會成功，且nickname允許全空白', 'user_token', 'user_nonce', 'nickname', '    ',  None,  '', 2),
            ('使用者再次更新自己的nickname距上次更新未超過30天應失敗', 'user_token', 'user_nonce', 'nickname', '🥰🥰🥰🥰❤️💞💝❤️💞💝',  'updateDB', (0-30*86400+1), 4),
            ('使用者更新自己的性別，值正確應成功', 'user_token', 'user_nonce', 'sex', 0,  None,  '', 2),
            ('使用者更新自己的性別是否公開的設定應成功', 'user_token', 'user_nonce', 'isPublicSexInfo', False, None, '', 2),
            ('使用者更新自己的個人簡介在100字之內應成功', 'user_token', 'user_nonce', 'description', '哈， I am richman!！！😂 😂 ',  None, '', 2),
            ('場控首次更新自己的nickname會成功', 'liveController1_token', 'liveController1_nonce', 'nickname', '🥰5566　-🥰',  None, '',  2),
            ('場控再次更新自己的nickname應成功', 'liveController1_token', 'liveController1_nonce', 'nickname', '🥰🥰🥰🥰❤️💞💝❤️💞💝', None, '', 2),
            ('場控修改個人簡介應成功', 'liveController1_token', 'liveController1_nonce', 'description', '我是場控',  None,  '', 2),
            ('使用者清空個人簡介應成功', 'user_token', 'user_nonce', 'description', '',  None,  '', 2),
            ('使用者設定自己生日為今天應成功', 'user_token', 'user_nonce', 'birthday', int(time.time()),  None,  '', 2),
            ('使用者更新自己的性別，但值不存在應錯誤', 'user_token', 'user_nonce', 'sex', 2,  None,  '', 4), 
            ('使用者再次更新自己的nickname距上次更新超過30天應成功', 'user_token', 'user_nonce', 'nickname', 'AB歡樂派！',  'updateDB', (0-30*86400-1), 2)
        ]  
    elif testName == 'newUser':
        #condition, expected
        testData = [
            ('regByMail', 2),
            ('loginByLine', 2)
        ]
    pprint(testData)
    return testData

'''
・檢測token/nonce取得對應帳號
'''
class TestGetMyInfo():
    def setup_class(self):
        sqlList = ["update identity set nickname = '' where id = '" + idList[0] + "'"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("token, nonce, account, role, expected", getData('getInfo'))
    def testGetInfo(self, token, nonce, account, role, expected):
        url = '/api/v2/identity/myInfo'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, url, 'get', None)
        restext = json.loads(res.text)
        pprint(res.json)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert restext['data']['roles'][0]['id'] == role
            assert restext['data']['loginId'] == test_parameter[account]
            assert len(restext['data']['trueLoveId']) > 0
            assert restext['data']['profilePicture'] in [
            'https://d1a89d7jvcvm3o.cloudfront.net/personal/d8b6498ba1119ff945bb2d9f9a33cfd1.jpeg',
            'https://d1a89d7jvcvm3o.cloudfront.net/personal/fadbe97ffce8c3b940e647ced2c81c87.jpeg',
            'https://d1a89d7jvcvm3o.cloudfront.net/personal/ec824bfe102a60882da1d54dfffd52a9.jpeg']
            assert restext['data']['nickname'] is not None
            

'''
・token/nonce判斷
・新註冊帳號新增對應資料
    isPasswordSet
    verifiedEmail
    verifiedPhone
    3rdPartySource
    3rdPartyInfo
・舊有帳號可以修改資料，若是空白則修改成空白
'''
class TestUpdateMyinfo():
    body = {'nickname': '123QQ', 'sex': 1, 'isPublicSexInfo': True, 'description': 'haha', 'birthday': int(time.time() - 5000)}
    @pytest.mark.parametrize("condition, expected", getData('newUser'))
    def testNewAccount(self, condition, expected):
        url = '/api/v2/identity/myInfo'
        if condition == 'regByMail':
            token, nonce, idToken = regByMail()
            header['X-Auth-Token'] = token
            header['X-Auth-Nonce'] = nonce
            header['Authorization'] = idToken
        elif condition == 'loginByLine':
            token, nonce, idToken = loginByLine()
            header['X-Auth-Token'] = token
            header['X-Auth-Nonce'] = nonce
            header['Authorization'] = idToken
        time.sleep(2)
        res = api.apiFunction(test_parameter['prefix'], header, url, 'get', None)
        restext = json.loads(res.text)
        if condition == 'regByMail':
            assert restext['data']['nickname'][0:4] == '初樂用戶'
            assert restext['data']['isPasswordSet'] == True
            assert restext['data']['verifiedEmail'] == 'tl-lisa@truelovelive.dev'
            assert len(restext['data']['trueLoveId']) > 0
        elif condition == 'loginByLine':
            assert restext['data']['nickname'][0:4] == '初樂用戶'
            assert restext['data']['3rdPartySource'] == 'Line'
            assert restext['data']['isPasswordSet'] == False
            assert len(restext['data']['trueLoveId']) > 0
            #print(restext['3rdPartyInfo'])

    @pytest.mark.parametrize("scenario, token, nonce, keyInfo, valueInfo, action, intervalSec, expected", getData('updateInfo'))
    def testUpdateInfo(self, scenario, token, nonce, keyInfo, valueInfo, action, intervalSec, expected):
        oriData = self.body[keyInfo]
        actionDic ={
            'updateDB':{'funcName': dbConnect.dbSetting,  'parameter': [test_parameter['db'], ["update nickname_reset set reset_time = date_add(reset_time, interval " + str(intervalSec) + " SECOND)"]]}
        }
        actionDic[action]['funcName'](*actionDic[action]['parameter']) if actionDic.get(action) else None
        url = '/api/v2/identity/myInfo'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        self.body[keyInfo] = valueInfo
        res = api.apiFunction(test_parameter['prefix'], header, url, 'put', self.body)
        assert res.status_code // 100 == expected
        if expected == 2:
            res = api.apiFunction(test_parameter['prefix'], header, url, 'get', None)
            restext = json.loads(res.text)
            assert restext['data'][keyInfo] == valueInfo
            assert len(restext['data']['trueLoveId']) > 0
            assert restext['data']['nickname'] == self.body['nickname']
            assert restext['data']['nicknameUpdateMsg'] == '每 30 天可修改 1 次 ，上次修改時間: yyyy/MM/dd'
        else:
            self.body[keyInfo] = oriData