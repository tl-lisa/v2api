#milestone 25 #1013 針對後台AD banner編輯管理，可做上下架時間設計
#milestone 28 #1819 加入cache機制(30秒)，另外需判斷start time及end time且以id desc排序
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
    400:{'Status': 'Error', 'Message': ['PARAM_TYPE_ERROR', 'ID_ERROR', 'PARAM_NOT_FOUND', 'LACK_OF_NECESSARY_PARAMS', 'QUERY_PARAMS_DIDNT_PAIRED']},
    404:{'Status': 'Error', 'Message': ['GIFT_CATAGORY_NOT_FOUND', 'MEDIA_NOT_FOUND']}
}
env = 'QA'
test_parameter = {}
idlist = []
ADData = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)   
    initdata.clearAD(test_parameter['db'])

#?zone=hot&type=0&item=20&page=1
#scenario, token, nonce, isCreate, condition, conditionDic, sleepTime, expected
testData = [
    ('權限正確無條件應該列出所有資料', 'user_token', 'user_nonce', '', {}, 0, 200),
    ('權限正確無條件應該列出所有資料', 'user_token', 'user_nonce', '', {}, 30, 200),
    ('權限正確條件為zone=hot', 'backend_token', 'backend_nonce', '?zoneType=HOT', {'bannerZone': 'HOT'}, 0, 200),
    ('權限正確條件為zone=NEW', 'backend_token', 'backend_nonce', '?zoneType=NEW', {'bannerZone': 'NEW'},  0, 200),
    ('權限正確條件為type=0', 'backend_token', 'backend_nonce', '?bannerType=0', {'bannerType': 0}, 0, 200),
    ('權限正確條件為zone=hot&type=2', 'broadcaster_token', 'broadcaster_nonce', '?zoneType=HOT&bannerType=2', {'bannerZone': 'HOT', 'bannerType': 2}, 0, 200),
    ('權限正確條件為zone=new&type=0', 'broadcaster_token', 'broadcaster_nonce', '?zoneType=NEW&bannerType=0', {'bannerZone': 'NEW', 'bannerType': 0}, 0, 200),
    ('權限正確條件但找不到資料為zone=event&type=1', 'broadcaster_token', 'broadcaster_nonce', '?zoneType=EVENT&bannerType=1', {'bannerZone': 'EVENT', 'bannerType': 1}, 0, 200),
    ('權限正確條件為參數未給值', 'backend_token', 'backend_nonce', '?zoneType=&bannerType=0', {'bannerType': 0}, 0, 400),
    ('權限不存在應該回失敗', 'err_token', 'err_nonce', '', {}, 0, 401)
]

@pytest.fixture(scope="class")
def creatAdBanner():
    initdata.clearAD(test_parameter['db'])
    #bannerZone, bannerType, bannerUrl, linkUrl, starttime diff, endtime diff
    bodyList = [
        ['HOT', 0, 'http://hot01.jpg','http://yahoo.com.tw', 100, 70],
        ['HOT', 2, 'http://hot21.jpg','http://yahoo.com.tw', -25, -120],
        ['NEW', 0, 'http://new01.jpg','http://yahoo.com.tw', 5, -55],
        ['TRACKING', 0, 'http://tracking01.jpg','http://yahoo.com.tw', 5, -60],
        ['EVENT', 0, 'http://event01.jpg','http://yahoo.com.tw', 5, -60],
        ['HOT', 0, 'http://hot02.jpg','http://yahoo.com.tw', 5, -30],
        ['HOT', 2, 'http://hot22.jpg','http://yahoo.com.tw', 5, -30],
        ['NEW', 0, 'http://new02.jpg','http://yahoo.com.tw', 5, -30],
        ['TRACKING', 0, 'http://tracking02.jpg','http://yahoo.com.tw', 5, -30],
        ['EVENT', 0, 'http://event01.jpg','http://yahoo.com.tw', 5, -30]
    ]
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    for i in bodyList:
        oriBody = {}
        oriBody['bannerZone'] = i[0]
        oriBody['bannerType'] = i[1]
        oriBody['bannerUrl'] = i[2]
        oriBody['linkUrl'] = i[3]
        oriBody['startTime'] = int(time.time()) - i[4]
        oriBody['endTime'] = int(time.time()) - i[5]
        api.apiFunction(test_parameter['prefix'], header, '/api/v2/backend/adBanner' , 'post', oriBody)
        time.sleep(1)
        sqlStr = "select max(id) from ad_banner"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        oriBody['id'] = result[0][0]
        ADData.append(oriBody)

class TestAdBanner():
    def checkResult(self, conditionDic, result, queryTime):
        global ADData
        source = []
        keyList = conditionDic.keys()
        for i in ADData:
            isAdd = False
            if all([i['startTime'] <= queryTime, i['endTime'] >= queryTime]):
                if keyList:
                    for j in keyList:
                        isAdd = True if i[j] == conditionDic[j] else False
                        if not isAdd:
                            break
                else:
                    isAdd = True
            source.append(i) if isAdd else print('not add')
        pprint(source)
        pprint(result)
        assert result['totalCount'] == len(source)
        for i in result:
            isExist = False
            for j in source:
                if j['id'] == j['id']:
                    assert j['bannerZone'] == j['bannerZone']
                    assert j['bannerType'] == j['bannerType']
                    assert j['linkUrl'] == j['linkUrl'] 
                    assert j['bannerUrl'] == j['bannerUrl']
                    assert j['startTime'] == j['startTime']
                    assert j['endTime'] == j['endTime']
                    isExist = True
                    break
            assert isExist 
 
    @pytest.mark.parametrize("scenario, token, nonce, condition, conditionDic, sleepTime, expected", testData)
    def testGetBanner(self, creatAdBanner, scenario, token, nonce, condition, conditionDic, sleepTime, expected):
        time.sleep(sleepTime)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/identity/adBanner/list' + condition
        queryTime = int(time.time())
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            if len(restext['data']) > 1:
                assert restext['data'][0]['id'] > restext['data'][1]['id']
            self.checkResult(conditionDic, restext, queryTime)
