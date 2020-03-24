#milestone19 email註冊流程 906/907
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
    tableList = ['identity_email_register_history', 'identity_profile']
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
        return([
                (False, ['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'lisa233152@gmail.com'], 'abc123', [2, 2, 2, 4, 4]),
                (False, ['tl-lisa@truelove', '@gmail.com', 'tlqa20200313@.com'], 'abc123', [4, 4, 4]),
                (False, 'tl-lisa@truelove.dev', ['1234', '123456789012345678901', '123嗨', '123!4', '1234 ', '1234😄'], [4, 4, 4, 4, 4, 4]),
                (True, ['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev'], 'abc123', [2, 4])
            ])  
    elif testName == 'mailCreateTime':
        #更改前2筆資料的create_at時間
        return([
                (['tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'tl-lisa@truelove.dev', 'lisa233152@gmail.com', 'lisa6335@hotmail.com'], 
                'abc123',
                [2, 2, 2, 2, 2, 4])
            ])
    elif testName == 'activeCode':
        return([
            (True, 'tokenWrong', 4),
            (False, 'codeWrong', 4),
            (False, 'expired', 4),
            (True, '', 2),
            (True, '', 4)
        ])

class TestSendEmail():
    head = {'Content-Type': 'application/json'}

    def teardown_function(self):
        sqlList = []
        sqlList.append("TRUNCATE TABLE identity_email_register_history")
        sqlList.append("alter table identity_email_register_history auto_increment = 1")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def runActiveCode(self, restext):
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        url = test_parameter['prefix'] + '/api/v2/identity/register/email/activate'
        body = {
             "tmpToken": tempToken,
             "activateCode": actCode
            }
        requests.post(url, headers=self.head, json=body) 

    @pytest.mark.parametrize("regEmail, PWD, expected", getTestData('mailCreateTime'))
    def testMailCreateTime(self, regEmail, PWD, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/register/email/send'
        for i in range(len(regEmail)):
            sqlList = [] 
            createTime = '' 
            body = {
                'email': regEmail[i],
                'password': PWD
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
                sqlList = ["update identity_email_register_history set created_at = '" + createTime + "' where id = select max(id) from identity_email_register_history"]
                dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("isRegister, regEmail, PWD, expected", getTestData('parameteType'))
    def testSend(self, isRegister, regEmail, PWD, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/register/email/send'
        if type(regEmail) == list:
            for i in range(len(regEmail)):
                body = {
                    'email': regEmail[i],
                    'password': PWD
                }
                res = requests.post(url, headers=self.head, json=body)     
                restext = json.loads(res.text)
                pprint(restext)
                assert res.status_code == expected[i]
                if isRegister and (res.status_code // 100 ==  2):
                    self.runActiveCode(json.loads(res.text))
            
        elif type(PWD) == list:
            for i in range(len(PWD)):
                body = {
                    'email': regEmail,
                    'password': PWD[i]
                }
                res = requests.post(url, headers=self.head, json=body)     
                restext = json.loads(res.text)
                pprint(restext)
                assert res.status_code == expected[i]

'''
啟用active code:
1.temptoken與active code不match
2.active code已經expired
3.active code錯誤
4.temptoken與active code皆正確
5.該mail已被註冊
'''
class TestActivateCode():
    head = {'Content-Type': 'application/json'}
    def getActiveCode(self):
        url = test_parameter['prefix'] + '/api/v2/identity/register/email/send'
        body = {
                    'email': 'tl-lisa@truelove.dev',
                    'password': '12345'
                }
        res = requests.post(url, headers=self.head, json=body)     
        restext = json.loads(res.text)     
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_email_register_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        return tempToken, actCode

    @pytest.mark.parametrize("isSendMail, condition, expected", getTestData('activeCode'))
    def testRegisterToActive(self, isSendMail, condition, expected):
        url = test_parameter['prefix'] + '/api/v2/identity/register/email/activate'
        if isSendMail:
            tempToken, actCode = self.getActiveCode()
        body = {
             "tmpToken": tempToken,
             "activateCode": actCode
            }
        if condition == 'tokenWrong':
            body["tmpToken"] = "wJalrXUtnFEMI..."
        elif condition == 'codeWrong':
            body["activateCode"] = "214520"
        elif condition == 'expired':
            sqlList = ['update identity_email_register_history set expires_in = 0  where id = (select max(id) from identity_email_register_history)']
            dbConnect.dbSetting(test_parameter['db'], sqlList)
        pprint(body)
        res = requests.post(url, headers=self.head, json=body) 
        assert res.status_code // 100 == expected
        if res.status_code // 100 == 2:
            restext = json.loads(res.text)
            checkList = ['nonce', 'token', 'idToken']
            for i in checkList:
                assert i in restext['data']
            
        
            
            
        
