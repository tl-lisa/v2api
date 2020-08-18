#milestone28新增此API #1160(如果token/nonce不正確或不存在則為401,若是權限問題則為403)
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
Msg = {
    200:{'Status': 'Ok', 'Message': 'SUCCESS'},
    401:{'Status': 'Error', 'Message': '使用者驗證錯誤，請重新登入'},
    400:{'Status': 'Error', 'Message': 'SOCKET_ERROR'},
    403:{'Status': 'Error', 'Message': '抱歉，您的使用權限不足！如有疑問，請洽初樂客服人員。'}
}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'], 
                        test_parameter['broadcaster1_acc']], idList)
                
def teardown_module ():
    api.change_user_mode(test_parameter['prefix'], idList[0], 1, 
        {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['backend_token'], 'X-Auth-Nonce': test_parameter['backend_nonce']})
    
testData = [
    ('使用broadcaster帳號呼叫,但chat server未開會回權限錯誤', 'broadcaster_token', 'broadcaster_nonce', 'stop', 400),
    ('chatServer正常使用broadcaster帳號呼叫會回成功', 'broadcaster_token', 'broadcaster_nonce', 'start', 200),
    ('chatServer正常使用broadcaster帳號被停權呼叫會回錯誤', 'broadcaster_token', 'broadcaster_nonce', 'suspended', 401),
    ('chatServer正常使用backend帳號呼叫會回權限錯誤', 'backend_token', 'backend_nonce', '', 403),
    ('chatServer正常使用user帳號呼叫會回權限錯誤', 'user_token', 'user_nonce', '', 403)
]

@pytest.mark.parametrize('scenario, token, nonce, action, expected', testData)
def testSerchUser(scenario, token, nonce, action, expected):
    actionDic = {
    'start': {'funName': sundry.setChatServer, 'parameter': [test_parameter['db'], 'sudo systemctl start tl-adapter.service tl-index.service']},
    'stop': {'funName': sundry.setChatServer, 'parameter': [test_parameter['db'], 'sudo systemctl stop tl-adapter.service tl-index.service']},
    'suspended':{'funName': api.change_user_mode, 'parameter': [test_parameter['prefix'], idList[0], -2, 
                {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': test_parameter['backend_token'], 'X-Auth-Nonce': test_parameter['backend_nonce']}]}
    }
    actionDic[action]['funName'](*actionDic[action]['parameter']) if actionDic.get(action) else None
    time.sleep(5)
    apiName = '/api/v2/liveMaster/loadBalance'
    header['X-Auth-Nonce'] = test_parameter[nonce]
    header['X-Auth-Token'] = test_parameter[token]
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    restext = json.loads(res.text)
    assert res.status_code == expected
    assert restext['Status'] == Msg[expected]['Status']
    assert restext['Message'] == Msg[expected]['Message']
    if expected == 200:
        assert len(restext['data']['socketIp']) > 0
        assert len(restext['data']['socketPort']) > 0