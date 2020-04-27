#mileston20 使用email or 手機發送驗證碼及驗證
#910(/api/v2/identity/password/verify)
#909 (/api/v2/identity/password/send)
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

env = 'testing'
test_parameter = {}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    
def emailReg(emailAddr, PWD):
    url = '/api/v2/identity/register/email/send'
    body = {
                'email': emailAddr,
                'password': PWD
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
    api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, url, 'post', body) 


def getTestData(testType):
    testData = []
    if testType == 'sendActive':
        #scenario, source, identifier, expected
        testData = [
            ('sendTimes', 'email', ['lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev', 'lisa@truelovelive.dev'], [2, 2, 2, 2, 4]),
            ('sendTimes', 'mobile', ['886-0988114885', '886-0988114885', '886-0988114885', '886-0988114885', '886-0988114885'], [2, 2, 2, 2, 4]),
            ('sourceWrong', 'sms', ['886-0988114885'], [4]),
            ('mailNotExist', 'email', ['list@trulovelive.dev'], [4]),
            ('mobileNoeExist', 'mobile', ['886-988114885', '88-0988114885', '0988114885'], [4, 4, 4])
        ]
    elif testType == 'verify':
        testData = [
            ('tokenWrong', 4),
            ('codeWrong', 4),
            ('notMatch', 4),
            ('expired', 4),
            ('success', 2)
        ]
    return testData

'''
send mail or sms:
mail及sms一週限制次數3次(分開計算)
email需已綁定；mobile需存在identity
'''

class TestSendActiveCode():
    def setup_class(self):
        initdata.clearIdentityData(test_parameter['db'])
        emailReg('lisa@truelovelive.dev', '123456')
        sqlList = ["update identity set phone_number = '0988114885', phone_country_code = '886' where login_id = 'track0050'"]
        sqlList.append('truncate table identity_pwd_reset_history')
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("scenario, source, identifier, expected", getTestData('sendActive'))
    def testSendMailOrSMS(self, scenario, source, identifier, expected):
        urlName = '/api/v2/identity/password/send'
        for i in range(len(identifier)):
            body = {
                "source": source,
                "identifier": identifier[i]
            }
            res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, urlName, 'post', body)
            assert res.status_code // 100 == expected[i]
            if expected[i] == 2:
                restext = json.loads(res.text)
                assert 'tmpToken' in restext['data']
                if i == 0:
                    createTime = (datetime.today() - timedelta(days=2+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d 15:59:59')
                    sqlStr = "select max(id) from identity_pwd_reset_history"
                    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                    sqlList = ["update identity_pwd_reset_history set created_at = '" + createTime + "' where id = " + str(result[0][0])]
                    dbConnect.dbSetting(test_parameter['db'], sqlList)
                    time.sleep(5)


'''
啟用active code:
temptoken與active code不match
active code已經expired
active code錯誤
temptoken與active code皆正確
'''

class TestVerify():
    info = []
    def setup_class(self):
        initdata.clearIdentityData(test_parameter['db'])
        emailReg('lisa@truelovelive.dev', '123456')
        sqlList = ["update identity set phone_number = '0988114885', phone_country_code = '886' where login_id = 'track0050'"]
        sqlList.append('truncate table identity_pwd_reset_history')
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def getActiveCode(self):
        urlName = '/api/v2/identity/password/send'
        body = {
                    'identifier': 'lisa@truelovelive.dev',
                    'source': 'email'
                }
        res = api.apiFunction(test_parameter['prefix'],{'Content-Type': 'application/json'}, urlName, 'post', body)  
        restext = json.loads(res.text)    
        tempToken = restext['data']['tmpToken']
        sqlStr = "select activate_code from identity_pwd_reset_history where token = '" + tempToken + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        actCode = result[0][0]
        self.info.append({"tmpToken": tempToken, "activateCode": actCode})
        return 

    @pytest.mark.parametrize("scenario, expected", getTestData('verify'))
    def testVerifyActive(self, scenario, expected):
        urlName = '/api/v2/identity/password/verify'
        body = {}
        if len(self.info) < 2:
            self.getActiveCode()
        if scenario == 'tokenWrong':
            body = {
                "tmpToken": "wJalrXUtnFEMI...",
                "activateCode": self.info[0]['activateCode']
            }
        elif scenario == 'codeWrong':
            body = {
                "tmpToken": self.info[0]['tmpToken'],
                "activateCode": '214324'
            }
        elif scenario == 'notMatch':
            body = {
                "tmpToken": self.info[0]['tmpToken'],
                "activateCode": self.info[1]['activateCode']
            }
        elif scenario == 'expired':
            sqlList = ["update identity_pwd_reset_history set expires_in = 0  where token = '" + self.info[0]['tmpToken'] + "'"]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
            body = {
                "tmpToken": self.info[0]['tmpToken'],
                "activateCode": self.info[0]['activateCode']
            }
        elif scenario == 'success':
            body = {
                "tmpToken": self.info[1]['tmpToken'],
                "activateCode": self.info[1]['activateCode']
            }
        
        res = api.apiFunction(test_parameter['prefix'], {'Content-Type': 'application/json'}, urlName, 'post', body)
        assert res.status_code // 100 == expected
        if res.status_code // 100 == 2:
            head = {'Content-Type': 'application/json', 'Connection': 'Keep-alive'}
            restext = json.loads(res.text)
            urlName = '/api/v2/identity/myInfo'
            head['X-Auth-Token'] = restext['data']['token']
            head['X-Auth-Nonce'] = restext['data']['nonce']
            res = api.apiFunction(test_parameter['prefix'], head, urlName, 'get', None)
            restext = json.loads(res.text)
            assert restext['data']['verifiedEmail'] == 'lisa@truelovelive.dev'
            