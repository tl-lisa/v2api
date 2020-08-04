# Milestone 17. 動態贈禮 - [GET] 後台讀取禮物清單 #773,動態贈禮 - [GET] 後台讀取禮物分類清單 #772,動態贈禮 - [POST] 後台新增禮物分類 #771
# Milestone 18. 動態贈禮 - 禮物分類（gift_category）需要追加軟刪除功能 #809 後台撈取禮物清單 API 更新 #811 後台撈取禮物分類列表 API 更新 #810
# milestone26 禮物類別新增category=5(聲聊) #1520 並於本次重構測試程式
import datetime
import json
import pytest
import time
from assistence import api
from assistence import initdata
from pprint import pprint
from datetime import datetime
from assistence import sundry
from assistence import dbConnect

env = 'QA'
BannerUrl = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
   

def teardown_module():
    pass

def getData(funType):
    testData = []
    if funType == 'add':
        #scenario, token, nonce, body, expected （由於必要欄位已由前端把關，故不驗）
        testData = [
            ('合法帳號建置直播間禮物類別(type=1)', 'backend_token', 'backend_nonce', {'categoryName':'直播間', 'type': 1, 'banner': BannerUrl, 'url':'https://www.truelovelive.com.tw/Index'}, 2),
            ('合法帳號建置liveshow禮物類別(type=2), 且banner為空字串', 'backend_token', 'backend_nonce', {'categoryName':'LiveShow', 'type': 2, 'banner': '', 'url':'https://www.truelovelive.com.tw/Index'}, 2),
            ('合法帳號建置動態禮物類別(type=3),且不存在url此key值', 'backend_token', 'backend_nonce', {'categoryName':'動態禮物', 'type': 3, 'banner': BannerUrl}, 2),
            ('合法帳號建置一對一私訊禮物類別(type=4),且不存在banner及url此key值', 'backend_token', 'backend_nonce', {'categoryName':'1V1', 'type': 4}, 2),
            ('合法帳號建置聲聊訊禮物類別(type=5),且不存在banner及url此key值', 'backend_token', 'backend_nonce', {'categoryName':'1V1', 'type': 4}, 2),
            #('客服帳號建置一對一私訊禮物類別(type=4),應失敗', 'liveController1_token', 'liveController1_nonce', {'categoryName':'1V1', 'type': 4}, 4), 
            ('權限不正確建置一對一私訊禮物類別(type=4),應失敗', 'err_token', 'err_nonce', {'categoryName':'1V1', 'type': 4}, 4)         
        ]
    elif funType == 'get':
        #scenario, token, nonce, action, condition, idList expected (delete 合併測試)
        testData = [
            ('若未指定statusFilter及typeFilter，會預設為all跟1', 'backend_token', 'backend_nonce', 'createData', '?item=3&page=1', [0,4,6], 2),
            ('未指定statusFilter預設為all,typeFilter=2', 'backend_token', 'backend_nonce', '', '?typeFilter=2&item=2&page=1', [1,5], 2),
            ('statusFilter＝all不會有封存的資料', 'backend_token', 'backend_nonce', 'delCategory', '?statusFilter=all&typeFilter=1&item=2&page=1', [4,6], 2),
            ('statusFilter＝on不會有封存的資料且現在時間介於start_time&end_time 之間', 'backend_token', 'backend_nonce', '', '?statusFilter=on&typeFilter=1&item=1&page=1', [6], 2),
            ('statusFilter=off不會有有封存的資料 OR now<start_time', 'backend_token', 'backend_nonce', '', '?statusFilter=off&item=1&page=1', [4], 2),
            ('statusFilter=off不會有封存的資料 OR now>end_time', 'backend_token', 'backend_nonce', '', '?statusFilter=off&typeFilter=2&item=1&page=1', [5], 2),
            ('statusFilter＝archive', 'backend_token', 'backend_nonce', '', '?statusFilter=archive&typeFilter=1&item=1&page=1', [0], 2),
            ('不合法的權限無法做資料查詢', 'err_token', 'err_nonce', '', '', [], 4)
        ]
    return testData  

class TestGiftCategory():
    categoryList = []
    def addData(self):
        dataList = [
            {'categoryName':'直播間1會被刪', 'type': 1, 'banner': BannerUrl, 'url':'https://www.truelovelive.com.tw/Index', 'startTime':int(time.time()) - 2, 'endTime': int(time.time()) + 10}, 
            {'categoryName':'LiveShow1在時間區間內', 'type': 2, 'banner': '', 'url':'https://www.truelovelive.com.tw/Index', 'startTime':int(time.time()) - 2, 'endTime': int(time.time()) + 10},
            {'categoryName':'動態禮物在時間區間內', 'type': 3, 'banner': BannerUrl, 'startTime':int(time.time()) - 2, 'endTime': int(time.time()) + 10},
            {'categoryName':'1V1在時間區間內', 'type': 4, 'startTime':int(time.time()) - 2, 'endTime': int(time.time()) + 10}, 
            {'categoryName':'直播間2；starttime>now', 'type': 1, 'banner': BannerUrl, 'url':'https://www.truelovelive.com.tw/Index', 'startTime':int(time.time()) + 5, 'endTime': int(time.time()) + 10}, 
            {'categoryName':'LiveShow2；endtime<now', 'type': 2, 'banner': '', 'url':'https://www.truelovelive.com.tw/Index', 'startTime':int(time.time()) - 8, 'endTime': int(time.time()) - 5},
            {'categoryName':'直播間3在時間區間內', 'type': 1, 'banner': BannerUrl, 'url':'https://www.truelovelive.com.tw/Index', 'startTime':int(time.time()) - 2, 'endTime': int(time.time()) + 10}
        ]
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        for i in dataList:
            res = api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/giftCategory', 'post', i)
            restext = json.loads(res.text)
            self.categoryList.append(restext['id'])

    def verifyAddResult(self, restext, body):
            typeList = ['live_room', 'live_show']
            assert restext['data'][0]['type'] == body['type']
            assert restext['data'][0]['categoryName'] == body['categoryName']
            assert restext['data'][0]['banner'] == body.get('banner')
            assert restext['data'][0]['url'] == body.get('url')
            assert restext['data'][0]['startTime'] == body['startTime']
            assert restext['data'][0]['endTime'] == body['endTime']
            if body['type'] in (1, 2):
                sqlStr = "select category_name, status, type, start_time, end_time from gift_category where id = " + str(restext['data'][0]['id'])
                result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                assert result[0][0] == body['categoryName']
                assert result[0][1] == 1
                assert result[0][2] == typeList[body['type'] - 1]
                assert result[0][3] == body['startTime'] * 1000
                assert result[0][4] == body['endTime'] * 1000

    @pytest.mark.parametrize("scenario, token, nonce, body, expected", getData('add'))
    def testAddCategory(self, scenario, token, nonce, body, expected):
        apiName = '/api/v2/backend/giftCategory'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        body['startTime'] = int(time.time()) - 2
        body['endTime'] = int(time.time()) + 3
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            sundry.clearCache(test_parameter['db'])
            res = api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/giftCategory/list?statusFilter=all&item=2&page=1&typeFilter=' + str(body['type']), 'get', None)
            restext = json.loads(res.text)
            self.verifyAddResult(restext, body)

    @pytest.mark.parametrize("scenario, token, nonce, action, condition, idList, expected", getData('get'))
    def testGetCategory(self, scenario, token, nonce, action, condition, idList, expected):
        if self.categoryList == []:
            id = '0'
        else:
            id = str(self.categoryList[0])
        actionDic = {
            'createData' : {'funName': self.addData},
            'delCategory': {'funName': api.apiFunction, 'parameter': [test_parameter['prefix'], header, '/api/v2/backend/giftCategory/'+id, 'delete', None]}
        }
        if action != '':
            if actionDic.get(action).get('parameter'):
                actionDic.get(action).get('funName')(*actionDic.get(action).get('parameter'))  
            else:
                actionDic.get(action).get('funName')()
        sundry.clearCache(test_parameter['db'])    
        expectList = [self.categoryList[i] for i in idList]
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/giftCategory/list' + condition
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            for i in restext['data']:
                assert i['id'] in expectList
 