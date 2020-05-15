#milestone19 email註冊流程 906/907
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
from pprint import pprint


env = 'QA'
test_parameter = {}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearIdentityData(test_parameter['db'])

'''
email註冊：
1.一週同email限制發送3次；正式上線會是10次
2.同IP不同email一週限制發送3次；正式上線會是10次
3.已註冊成功的email要求發送會錯誤
4.已綁定的email要求發送會錯誤
5.email格式不正確
6.password格式不正確（僅驗證長度）
'''

def getTestData(testName):
    if testName == 'parameteType':
        #regEmail是一個list或字串，用來模擬多次行為 
        #PWD是一個list或字串，用來模擬多次行為 
        return([
                (False, ['lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev'], 'abc123', [2, 2, 2, 4]),
                (False, ['@gmail.com', 'tl-lisa@truelove', 'tlqa20200313@.com'], 'abc123', [4, 4, 4]),
                (False, 'lisa@truelovelive.dev', ['1234', '123456789012345678901', '123嗨', '123!4', '12 34', '1234😄', '!@！1'], [4, 4, 4, 4, 4, 4, 4]),
                (True, ['lisa@truelovelive.dev', 'lisa@truelovelive.dev'], 'abc123', [2, 4])
            ])  
    elif testName == 'mailCreateTime':
        #更改前2筆資料的create_at時間
        return([
                (['lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev'], 
                'abc123',
                [2, 2, 2, 2, 2, 4])
            ])
    elif testName == 'activeCode':
        return([
            ('tokenWrong', 4),
            ('codeWrong', 4),
            ('expired', 4),
            ('wihtoutPushToken', 2),
            ('success', 2)
        ])

#@pytest.mark.skip()
class TestSendEmail():
    head = {'Content-Type': 'application/json'}

    def runActiveCode(self, restext):
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        url = '/api/v2/identity/register/email/activate'
        body = {
            "tmpToken": tempToken,
            "activateCode": actCode,
            "pushToken":"emailRegrjhjayegrkldfkhgdkfasd"
        } 
        pprint(body)
        api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)
        
    #@pytest.mark.skip()
    @pytest.mark.parametrize("regEmail, PWD, expected", getTestData('mailCreateTime'))
    def testMailCreateTime(self, regEmail, PWD, expected):
        url = '/api/v2/identity/register/email/send'
        for i in range(len(regEmail)):
            sqlList = [] 
            createTime = '' 
            body = {
                'email': regEmail[i],
                'password': PWD
            }
            print(body)
            res = api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body) 
            assert res.status_code // 100 == expected[i]
            if i == 0:
                createTime = (datetime.today() - timedelta(days=8+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            elif i == 1:
                createTime = (datetime.today() - timedelta(days=2+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 15:59:59')
            elif i == 2:
                createTime = (datetime.today() - timedelta(days=2+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            if len(createTime) > 0:
                sqlStr = "select max(id) from identity_email_register_history"
                result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                sqlList = ["update identity_email_register_history set created_at = '" + createTime + "' where id = " + str(result[0][0])]
                dbConnect.dbSetting(test_parameter['db'], sqlList)

   
    @pytest.mark.parametrize("isRegister, regEmail, PWD, expected", getTestData('parameteType'))
    def testSend(self, isRegister, regEmail, PWD, expected):
        initdata.clearIdentityData(test_parameter['db'])
        url = '/api/v2/identity/register/email/send'
        if type(regEmail) == list:
            for i in range(len(regEmail)):
                body = {
                    'email': regEmail[i],
                    'password': PWD
                }
                res = api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)
                assert res.status_code // 100 == expected[i]
                if isRegister and (res.status_code // 100 ==  2):
                    self.runActiveCode(json.loads(res.text))
            
        elif type(PWD) == list:
            for i in range(len(PWD)):
                body = {
                    'email': regEmail,
                    'password': PWD[i]
                }
                res = api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)    
                assert res.status_code // 100 == expected[i]

'''
啟用active code:
temptoken與active code不match
active code已經expired
active code錯誤
temptoken與active code皆正確
該mail已被註冊
'''

#@pytest.mark.skip()
class TestActivateCode():
    head = {'Content-Type': 'application/json'}
    def setup_method(self):
        initdata.clearIdentityData(test_parameter['db'])

    def getActiveCode(self):
        url = '/api/v2/identity/register/email/send'
        body = {
                    'email': 'lisa@truelovelive.dev',
                    'password': '12345',
                    'pushToken': 'emailRegrjhjayegrkldfkhgdkfasd'
                }
        res = api.apiFunction(test_parameter['prefix'],{'Content-Type': 'application/json'}, url, 'post', body)  
        restext = json.loads(res.text)    
        pprint(restext) 
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        return tempToken, actCode

    @pytest.mark.parametrize("condition, expected", getTestData('activeCode'))
    def testRegisterToActive(self, condition, expected):
        url = '/api/v2/identity/register/email/activate'
        tempToken, actCode = self.getActiveCode() 
        body = {
             "tmpToken": tempToken,
             "activateCode": actCode,
             "pushToken": "emailRegrjhjayegrkldfkhgdkfasd"
            }
        if condition == 'tokenWrong':
            body["tmpToken"] = "wJalrXUtnFEMI..."
        elif condition == 'codeWrong':
            body["activateCode"] = "214520"
        elif condition == 'wihtoutPushToken':
            body["pushToken"] = ""
        elif condition == 'expired':
            sqlStr = "select max(id) from identity_email_register_history"
            result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            sqlList = ["update identity_email_register_history set expires_in = 1  where id = " + str(result[0][0])]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
            time.sleep(2)
        pprint(condition)
        res = api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)
        assert res.status_code // 100 == expected
        if res.status_code // 100 == 2:
            restext = json.loads(res.text)
            checkList = ['nonce', 'token', 'idToken']
            for i in checkList:
                assert i in restext['data']
            
        
            
            
        
