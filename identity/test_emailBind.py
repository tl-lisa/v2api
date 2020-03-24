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
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

env = 'testing'
test_parameter = {}
mailList = ['tl-lisa@truelove.dev', 'tlqa20200313@gmail.com', 'lisa233152@gmail.com']


def setup_module():
    initdata.set_test_data(env, test_parameter)

def teardown_module():
    sqlList = []
    tableList = ['identity_email_bind_history', 'identity_profile']
    sqlStr = 'select identity_id from identity_profile'
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
                (False, ['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'lisa233152@gmail.com'], [2, 2, 2, 4, 4]),
                (False, ['tl-lisa@truelove', '@gmail.com', 'tlqa20200313@.com'], [4, 4, 4]),
                (True, ['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev'], [2, 4])
            ])  
    elif testName == 'mailCreateTime':
        #更改前2筆資料的create_at時間
        return([
                (['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'lisa233152@gmail.com', 'lisa6335@hotmail.com'], 
                'abc123',
                [2, 2, 2, 2, 2, 4])
            ])
    elif testName == 'activeCode':
        #"isSendMail, condition, bindMail, PWD, expected"
        return([
            (True, 'sourceWrong', 'tl-lisa@truelove.dev', ['1234a'], [4]),
            (False, 'codeWrong', 'tl-lisa@truelove.dev', ['1234a'], [4]),
            (False, 'codeExpired', 'tl-lisa@truelove.dev', ['1234a'], [4]),
            (False, 'mailDismatch', 'tl-lisa@truelove.dev', ['1234a'],[4]),
            (False, '', 'tl-lisa@truelove.dev',  ['1234', '123456789012345678901', '123嗨', '123!4', '1234 ', '1234😄', ''],[4]),
            (True, '', 'tl-lisa@truelove.dev', ['1234a'], [2]),
            (True, '', 'lisa233152@gmail.com', ['1234a'], [4])
        ])

class TestSendEmail():
    head = {'Content-Type': 'application/json'}

    def teardown_function(self):
        sqlList = []
        sqlList.append("TRUNCATE TABLE identity_email_bind_history")
        sqlList.append("alter table identity_email_bind_history auto_increment = 1")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def runActiveCode(self, restext):
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_email_bind_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        url = test_parameter['prefix'] + '/api/v2/identity/binding/email/activate'
        body = {
             "tmpToken": tempToken,
             "activateCode": actCode
            }
        requests.post(url, headers=self.head, json=body) 

    @pytest.mark.parametrize("regEmail, PWD, expected", getTestData('mailCreateTime'))
    def testMailCreateTime(self, regEmail, PWD, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/binding/email/send'
        for i in range(len(regEmail)):
            sqlList = [] 
            createTime = '' 
            body = {
                'email': regEmail[i]
            }
            res = requests.post(url, headers=self.head, json=body)     
            restext = json.loads(res.text)
            pprint(restext)
            assert res.status_code == expected[i]
            if i == 0:
                createTime = (datetime.today() - timedelta(days=7+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            elif i == 1:
                createTime = (datetime.today() - timedelta(days=datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 15:59:59')
            elif i == 2:
                createTime = (datetime.today() - timedelta(days=datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 16:00:00')
            if len(createTime) > 0:
                sqlList = ["update identity_email_bind_history set created_at = '" + createTime + "' where id = select max(id) from identity_email_bind_history"]
                dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("isBinded, bindEmail, expected", getTestData('parameteType'))
    def testSend(self, isBinded, bindEmail, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/binding/email/send'
        for i in range(len(bindEmail)):
            body = {
                'email': bindEmail[i]
            }
            res = requests.post(url, headers=self.head, json=body)     
            restext = json.loads(res.text)
            pprint(restext)
            assert res.status_code == expected[i]
            if isBinded and (res.status_code // 100 ==  2):
                self.runActiveCode(json.loads(res.text))
            
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
class TestActivateCode():
    head = {'Content-Type': 'application/json'}
    def getActiveCode(self, bindMail):
        url = test_parameter['prefix'] + '/api/v2/identity/binding/email/send'
        body = {
                    'email': bindMail
                }
        requests.post(url, headers=self.head, json=body)     
        sqlStr = "select activate_code from identity_email_bind_history where id = (select max(id) from identity_email_bind_history)"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        return actCode

    @pytest.mark.parametrize("isSendMail, condition, bindMail, PWD, expected", getTestData('activeCode'))
    def testBindToActive(self, isSendMail, condition, bindMail, PWD, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/binding/email/activate'
        if isSendMail:
            actCode = self.getActiveCode(bindMail)
        for i in range(len(bindMail)):
            body = {
                "source": "advance",
                "email": bindMail[i],
                "password": PWD,
                "activateCode": actCode
            }
            if condition == 'sourceWrong':
                body["source"] = "test123"
            elif condition == 'codeWrong':
                body["activateCode"] = "214520"
            elif condition == 'mailDismatch':
                body["email"] = "lisa@hotmial.com"
            elif condition == 'codeExpired':
                sqlList = ['update identity_email_bind_history set expires_in = 0 where id = (select max(id) from identity_email_bind_history)']
                dbConnect.dbSetting(test_parameter['db'], sqlList)
            pprint(body)
            res = requests.post(url, headers=self.head, json=body) 
            assert res.status_code // 100 == expected[i]