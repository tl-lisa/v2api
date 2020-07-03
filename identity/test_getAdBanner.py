#milestone 25 #1013 針對後台AD banner編輯管理，可做上下架時間設計
import json
import requests
import pymysql
import time
import string
import threading
import socket
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from assistence import sundry

Msg = {
    200:{'Status': 'Ok', 'Message': 'SUCCESS'},
    401:{'Status': 'Error', 'Message': ['使用者驗證錯誤，請重新登入', 'AUTH_ERROR']},
    403:{'Status': 'Error', 'Message': ['PERMISSION_REQUIRED', 'FORBIDDEN_TO_AUTH', '抱歉，您的使用權限不足！如有疑問，請洽初樂客服人員。']},
    400:{'Status': 'Error', 'Message': ['PARAM_TYPE_ERROR', 'ID_ERROR', 'PARAM_NOT_FOUND', 'LACK_OF_NECESSARY_PARAMS']},
    404:{'Status': 'Error', 'Message': ['GIFT_CATAGORY_NOT_FOUND', 'MEDIA_NOT_FOUND']}
}
env = 'QA'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)   
    initdata.clearAD(test_parameter['db'])

#?zone=hot&type=0&item=20&page=1
#scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected
testData = [
    ('權限正確無條件應該列出所有資料', 'user_token', 'user_nonce', True, '', '', '', 10, 5, 200),
    ('權限正確條件為zone=hot', 'backend_token', 'backend_nonce', False, '?zoneType=hot', 'bannerZone', 'hot', 10, 2, 200),
    ('權限正確條件為type=0', 'backend_token', 'backend_nonce', False, '?bannerType=0', 'bannerType', 0, 10, 4, 200),
    ('權限正確條件為zone=hot&type=2', 'broadcaster_token', 'broadcaster_nonce', False, '?zoneType=hot&bannerType=2', 'bannerType', 2, 10, 1, 200),
    ('權限正確條件為zone=new&type=2', 'broadcaster_token', 'broadcaster_nonce', False, '?zoneType=new&bannerType=2', '', '', 10, 0, 200),
    ('權限正確條件為參數錯誤', 'backend_token', 'backend_nonce', False, '?bannerzone=new&bannerType=2', '', '', 10, 0, 400),
    ('權限正確條件為參數未給值', 'backend_token', 'backend_nonce', False, '?zoneType=&bannerType=2', '', '', 10, 0, 400),
    ('權限不存在應該回失敗', 'err_token', 'err_nonce', False, '', '', '', 10, 5, 401)
]

class TestAdBanner():
    oriBody = {}
    def setup_method(self):
        sundry.clearCache(test_parameter['db'])
    
    def checkResult(self, source, result):
        assert result['bannerZone'] == source['bannerZone']
        assert result['bannerType'] == source['bannerType']
        assert result['linkUrl'] == source['linkUrl']
        assert result['bannerUrl'] == source['bannerUrl']
        assert result['startTime'] == source['startTime']
        assert result['endTime'] == source['endTime']
 
    def creatAdBanner(self, count):
        initdata.clearAD(test_parameter['db'])
        #bannerZone, bannerType, bannerUrl, linkUrl
        bodyList = [
            ['hot', 0, 'http://hot0.jpg','http://yahoo.com.tw'],
            ['hot', 2, 'http://hot2.jpg','http://yahoo.com.tw'],
            ['new', 0, 'http://new0.jpg','http://yahoo.com.tw'],
            ['tracking', 0, 'http://tracking0.jpg','http://yahoo.com.tw'],
            ['event', 0, 'http://event0.jpg','http://yahoo.com.tw']
        ]
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        for i in range(count):
            self.oriBody.clear()
            self.oriBody['bannerZone'] = bodyList[i][0]
            self.oriBody['bannerType'] = bodyList[i][1]
            self.oriBody['bannerUrl'] = bodyList[i][2]
            self.oriBody['linkUrl'] = bodyList[i][3]
            self.oriBody['startTime'] = int(time.time())
            self.oriBody['endTime'] = int(time.time()) + 3600 
            api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/adBanner' , 'post', self.oriBody)
            time.sleep(1)

    @pytest.mark.parametrize("scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected", testData)
    def testGetBanner(self, scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected):
        self.creatAdBanner(5) if isCreate else None
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/adBanner/list' + condition
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            assert restext['totalCount'] == totalCount
            assert len(restext['data']) <= items
            if key != '':
                for i in restext['data']:
                    assert i[key] == value
