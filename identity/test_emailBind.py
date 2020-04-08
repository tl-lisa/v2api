#milestone19 email綁定流程中，用既有帳號做驗證 861/862
import json
import requests
import pymysql
import pytest
import time
import string
from datetime import datetime, timedelta
from ..assistence import dbConnect
from ..assistence import initdata
from ..assistence import api
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

env = 'testing'
test_parameter = {}
mailList = ['lisa@truelovelivelive.dev', 'tlqa20200313@gmail.com', 'lisa233152@gmail.com']

def clearData():
    sqlList = []
    tableList = ['identity_email_bind_history', 'identity_profile']
    sqlStr = 'select identity_id from identity_profile'
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    print(len(result))
    for i in tableList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)       
    for i in range(len(result)):
        for j in range(len(result[i])):
            if j == 0:
                sqlStr = "delete from identity where id in ('"
            sqlStr += result[i][j] 
            if len(result[i]) - j == 1:
                sqlStr += "')"
            else:
                sqlStr += "', '"
        sqlList.append(sqlStr)
    sqlList.append("alter table " + tableList[0] + " auto_increment = 1") 
    dbConnect.dbSetting(test_parameter['db'], sqlList)

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
        #isBinded, bindEmail, expected
        return([
                (False, ['lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev'], [2, 2, 2, 4]),
                (False, ['lisa@truelovelive', '@gmail.com', 'tlqa20200313@.com'], [4, 4, 4]),
                (True, ['lisa@truelovelive.dev', 'lisa@truelovelive.dev'], [2, 4])
            ])  
    elif testName == 'mailCreateTime':
        #更改前2筆資料的create_at時間
        return([
                (['lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev'], 
                'abc123',
                [2, 2, 2, 2, 2, 4])
            ])
    elif testName == 'activeCode':
        #"isSendMail, condition, bindMail, PWD, expected"
        return([
            #(True, 'sourceWrong', 'lisa@truelovelive.dev', '1234a', 4),
            (True, 'codeWrong', 'lisa@truelovelive.dev', '1234a', 4),
            (False, 'codeExpired', 'lisa@truelovelive.dev', '1234a', 4),
            (False, 'mailDismatch', 'lisa@truelovelive.dev', '1234a',4),
            (False, '', 'lisa@truelovelive.dev',  ['1234', '123456789012345678901', '123嗨', '123!4', '1234 ', '1234😄', ''], 4)
           # (True, '', 'lisa@truelovelive.dev', '123456', 2)
        ])


#@pytest.mark.skip()
class TestSendEmail():
    head = {'Content-Type': 'application/json', 'X-Auth-Token': '', 'X-Auth-Nonce': '', 'Authorization': ''}
    def setup_class(self):
        '''
        url = #'/api/v2/identity/auth/login'
        body = {
            "account": "track0050",
            "password": "123456",
            "pushToken":"dshfklkrjhjayegrkldfkhgdkfasd"
        }
        
        res =  api.apiFunction(test_parameter['prefix'], {}, url, 'post', body) 
        restext = json.loads(res.text)
        self.head['X-Auth-Token'] = restext['data']['token']
        self.head['X-Auth-Nonce'] = restext['data']['nonce']
        self.head['Authorization'] = restext['data']['idToken']
        '''
        self.head['X-Auth-Token'] = test_parameter['user_token']
        self.head['X-Auth-Nonce'] = test_parameter['user_nonce']

    def runActiveCode(self, bindMail):
        sqlStr = "select activate_code from identity_email_bind_history where id = (select max(id) from identity_email_bind_history)"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        url = '/api/v2/identity/binding/email/activate'
        body = {
            "source": "advance",
            "email": bindMail,
            "password": '123456',
            "activateCode": actCode
        }
        api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)

    @pytest.mark.parametrize("regEmail, PWD, expected", getTestData('mailCreateTime'))
    def testMailCreateTime(self, regEmail, PWD, expected):
        url = '/api/v2/identity/binding/email/send'
        for i in range(len(regEmail)):
            sqlList = [] 
            createTime = '' 
            body = {
                'email': regEmail[i]
            }
            res =  api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body) 
            restext = json.loads(res.text)
            pprint(restext)
            assert res.status_code // 100 == expected[i]
            if i == 0:
                createTime = (datetime.today() - timedelta(days=8+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            elif i == 1:
                createTime = (datetime.today() - timedelta(days=2+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 15:59:59')
            elif i == 2:
                createTime = (datetime.today() - timedelta(days=2+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            if len(createTime) > 0:
                sqlStr = "select max(id) from identity_email_bind_history"
                result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                sqlList = ["update identity_email_bind_history set created_at = '" + createTime + "' where id = " + str(result[0][0])]
                dbConnect.dbSetting(test_parameter['db'], sqlList)
            time.sleep(20)

    @pytest.mark.parametrize("isBinded, bindEmail, expected", getTestData('parameteType'))
    def testSend(self, isBinded, bindEmail, expected):
        initdata.clearIdentityData(test_parameter['db'])
        url = '/api/v2/identity/binding/email/send'
        for i in range(len(bindEmail)):
            body = {
                'email': bindEmail[i]
            }
            res = api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)  
            restext = json.loads(res.text)
            pprint(restext)
            assert res.status_code // 100 == expected[i]
            if isBinded and (res.status_code // 100 ==  2):
                self.runActiveCode(bindEmail[i])
            time.sleep(20)
            
'''
啟用active code:
1.password 檢查
2.active code已經expired
3.active code錯誤
5.email與active code不match
4.active code皆正確
5.該mail已被註冊
6.來源別不存在
'''
#@pytest.mark.skip()
class TestActivateCode():
    head = {'Content-Type': 'application/json', 'X-Auth-Token': '', 'X-Auth-Nonce': '', 'Authorization': ''}
    def setup_class(self):
        '''
        url = '/api/v2/identity/auth/login'
        body = {
            "account": "track0050",
            "password": "123456",
            "pushToken":"dshfklkrjhjayegrkldfkhgdkfasd"
        } 
        res = api.apiFunction(test_parameter['prefix'], {}, url, 'post', body)
        restext = json.loads(res.text)
        self.head['X-Auth-Token'] = restext['data']['token']
        self.head['X-Auth-Nonce'] = restext['data']['nonce']
        self.head['Authorization'] = restext['data']['idToken']
        '''
        self.head['X-Auth-Token'] = test_parameter['user_token']
        self.head['X-Auth-Nonce'] = test_parameter['user_nonce']
        initdata.clearIdentityData(test_parameter['db'])

    def getActiveCode(self, bindMail):
        url = '/api/v2/identity/binding/email/send'
        body = {
                    'email': bindMail
                }
        api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body)  
        sqlStr = "select max(id) from identity_email_bind_history"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)       
        sqlStr = "select activate_code from identity_email_bind_history where id = " + str(result[0][0])
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        #pprint(result)
        return result[0][0]

    @pytest.mark.parametrize("isSendMail, condition, bindMail, PWD, expected", getTestData('activeCode'))
    def testBindToActive(self, isSendMail, condition, bindMail, PWD, expected):
        actCode = 0
        url = '/api/v2/identity/binding/email/activate'
        if isSendMail:
            actCode = self.getActiveCode(bindMail)
            time.sleep(20)
        body = {
            "source": "advance",
            "email": bindMail,
            "activateCode": actCode
        }    
        if condition == 'sourceWrong':
            body["source"] = "test"
        elif condition == 'codeWrong':
            body["activateCode"] = "214520"
        elif condition == 'mailDismatch':
            body["email"] = "lisa@hotmial.com"
        elif condition == 'codeExpired':
            sqlStr = "select max(id) from identity_email_bind_history"
            result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            sqlList = ["update identity_email_bind_history set expires_in = 0 where id = " + str(result[0][0])]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
        if type(PWD) == list:
            for i in range(len(PWD)):
                body["password"] = PWD[i]
                res =  api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body) 
                assert res.status_code // 100 == expected
        else:
            body["password"] = PWD
            pprint(body)
            res =  api.apiFunction(test_parameter['prefix'], self.head, url, 'post', body) 
            assert res.status_code // 100 == expected