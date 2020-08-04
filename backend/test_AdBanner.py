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

def getTestData(testName): 
    testData = []
    body =  {
        "linkUrl": "https://truelovelive.com.tw", "bannerUrl": "http//hot1.123", "bannerZone": "HOT",
        "bannerType": 0, "startTime": int(time.time()), "endTime":int(time.time()) + 3600
    }
    if testName == 'add': 
        #scenario, token, nonce, body, expected
        testData = [
            ('正確的權限新增資料應成功', 'backend_token', 'backend_nonce', body, 200), 
            ('不正確的權限新增資料應失敗', 'liveController1_token', 'liveController1_nonce', body, 403),
            ('不存在的token/nonce新增資料應失敗', 'err_token', 'err_nonce', body, 401)
        ]         
    elif testName == 'get':
        #?zone=hot&type=0&item=20&page=1
        #scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected
        testData = [
            ('權限正確無條件應該列出所有資料', 'backend_token', 'backend_nonce', True, '', '', '', 10, 5, 200),
            ('權限正確條件為item=1&page=1', 'backend_token', 'backend_nonce', False, '?item=1&page=1', 'id', 5, 1, 5, 200),
            ('權限正確條件為item=1&page=2', 'backend_token', 'backend_nonce', False, '?item=1&page=2', 'id', 4, 1, 5, 200),
            ('權限正確條件為zone=hot&item=10&page=1', 'backend_token', 'backend_nonce', False, '?zone=HOT&item=10&page=1', 'bannerZone', 'HOT', 10, 2, 200),
            ('權限正確條件為type=0&item=10&page=1', 'backend_token', 'backend_nonce', False, '?type=0&item=10&page=1', 'bannerType', 0, 10, 4, 200),
            ('權限正確條件為zone=hot&type=2&item=10&page=1', 'backend_token', 'backend_nonce', False, '?zone=HOT&type=2&item=10&page=1', 'bannerType', 2, 10, 1, 200),
            ('權限正確條件為zone=new&type=2&item=10&page=1', 'backend_token', 'backend_nonce', False, '?zone=NEW&type=2&item=10&page=1', '', '', 10, 0, 200),
            ('權限正確條件為參數錯誤', 'backend_token', 'backend_nonce', False, '?bannerzone=NEW&type=2&item=10&page=1', '', '', 10, 0, 400),
            ('權限正確條件為參數未給值', 'backend_token', 'backend_nonce', False, '?zone=&type=2&item=10&page=1', '', '', 10, 0, 400),
            ('權限不正確應該回失敗', 'liveController1_token', 'liveController1_nonce', False, '', '', '', 10, 5, 403),
            ('權限不存在應該回失敗', 'err_token', 'err_nonce', False, '', '', '', 10, 5, 401)
        ]
    elif testName == 'edit': 
        #scenario, token, nonce, isCreate, id, key, value, expected
        testData = [
            ('新增資料且權限正確針對linkUrl進行修改，結果應成功', 'backend_token', 'backend_nonce', True, 1, 'linkUrl', 'https://yahoo.com.tw', 200),
            ('權限正確針對bannerUrl進行修改，結果應成功', 'backend_token', 'backend_nonce', False, 1, 'bannerUrl', 'https://bannerUrl.com.tw', 200),
            ('權限正確針對bannerType進行修改，結果應成功', 'backend_token', 'backend_nonce', False, 1, 'bannerType', 2, 200),
            ('權限正確針對bannerZone進行修改，結果應成功', 'backend_token', 'backend_nonce', False, 1, 'bannerZone', 'NEW', 200),
            ('權限正確針對startTime進行修改，結果應成功', 'backend_token', 'backend_nonce', False, 1, 'startTime', int(time.time()) + 300, 200),
            ('權限正確針對endTime進行修改，結果應成功', 'backend_token', 'backend_nonce', False, 1, 'endTime', int(time.time()) + 7200, 200),
            ('權限正確但ID不存在，結果應失敗', 'backend_token', 'backend_nonce', False, 9, 'endTime', int(time.time()) + 7200, 400),
            ('權限不正確針對endTime進行修改，結果應失敗', 'liveController1_token', 'liveController1_nonce', False, 1, 'endTime', int(time.time()) + 7200, 403),
            ('token/nonce不存在針對endTime進行修改，結果應失敗', 'err_token', 'err_nonce', False, 1, 'endTime', int(time.time()) + 7200, 401)
        ]
    elif testName == 'del':
        #scenario, token, nonce, isCreate, id, expected
        testData = [
            ('正確的權限刪除資料應成功', 'backend_token', 'backend_nonce', True, 1, 200), 
            ('正確的權限刪除id不存在應失敗', 'backend_token', 'backend_nonce', False, 99, 400), 
            ('不正確的權限刪除資料應失敗', 'liveController1_token', 'liveController1_nonce', False, 2, 403),
            ('不存在的token/nonce刪除資料應失敗', 'err_token', 'err_nonce', False, 2, 401)
        ]          
    return testData


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
            ['HOT', 0, 'http://hot0.jpg','http://yahoo.com.tw'],
            ['HOT', 2, 'http://hot2.jpg','http://yahoo.com.tw'],
            ['NEW', 0, 'http://new0.jpg','http://yahoo.com.tw'],
            ['TRACKING', 0, 'http://tracking0.jpg','http://yahoo.com.tw'],
            ['EVENT', 0, 'http://event0.jpg','http://yahoo.com.tw']
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

    @pytest.mark.parametrize("scenario, token, nonce, body, expected", getTestData('add'))
    def testAddBanner(self, scenario, token, nonce, body, expected):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/adBanner' 
        body['startTime'] = int(time.time())
        body['endTime'] = int(time.time()) + 3600
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            res = api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/adBanner/list', 'get', None)
            restext = json.loads(res.text)
            self.checkResult(body, restext['data'][0])

    @pytest.mark.parametrize("scenario, token, nonce, isCreate, id, key, value, expected", getTestData('edit'))
    def testEditBanner(self, scenario, token, nonce, isCreate, id, key, value, expected):
        self.creatAdBanner(1) if isCreate else None
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/adBanner/' + str(id) 
        self.oriBody[key] = value
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'patch', self.oriBody)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            res = api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/adBanner/list', 'get', None)
            restext = json.loads(res.text)
            self.checkResult(self.oriBody, restext['data'][0])

    @pytest.mark.parametrize("scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected", getTestData('get'))
    def testGetBanner(self, scenario, token, nonce, isCreate, condition, key, value, items, totalCount, expected):
        self.creatAdBanner(5) if isCreate else None
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/adBanner/list' + condition
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

    @pytest.mark.parametrize("scenario, token, nonce, isCreate, id, expected", getTestData('del'))
    def testDelBanner(self, scenario, token, nonce, isCreate, id, expected):
        idlist = []
        self.creatAdBanner(1) if isCreate else None
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/adBanner/' + str(id) 
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            res = api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/adBanner/list', 'get', None)
            restext = json.loads(res.text)
            for i in restext['data']:
                idlist.append(i['id'])
            assert id not in idlist