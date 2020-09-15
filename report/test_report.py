#milestone18 加入動態贈禮
#milestone26 加入小遊戲點數計算 重構所有點數計算方式
#milestone30 後台新增2張報表，完全比照ranking的輸入/輸出 #1925/1926
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
from datetime import datetime, timedelta
from operator import itemgetter
from report import setTestData

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
userList = ['46a10b92-e067-4fd3-ad13-e30f94410052', '774ab73f-6aa6-4ed1-a991-609d7db7d1a3'] #track0040, track0050
masterList = ['d82a7ba2-5c11-4615-aba7-2a768d927165', '971f5a08-a8df-493a-93ca-8df6022963de', 'ff0538bd-0657-45b5-9eaa-b298f99d5269', '42fa6c81-5cfa-4b03-8263-ff45a153b0f1'] #broadcaster005~007; 004
db = '35.234.17.150'
result = {}

@pytest.fixture(scope='session')
def testInitial():
    global result
    result = setTestData.getData(userList, masterList, db)
    #pprint(result)

def setup_module():
    initdata.set_test_data(env, test_parameter) 

def getTestData(funName):
    testData = []
    if funName == 'revenue':
        testData = [
            ('一般直播主開播時數最多3小時，且本日及昨日可以立即查詢', 'broadcaster_token', 'broadcaster_nonce', masterList[0], 2),
            ('一般直播主未開播但有收禮，本日及昨日可以立即查詢', 'broadcaster1_token', 'broadcaster1_nonce', masterList[1], 2),
            ('一般直播主開播時數最多3小時，且有效時數不得大於實際開播時數', 'broadcaster3_token', 'broadcaster3_nonce', masterList[3], 2),
            ('二次元直播主有開播開播時數最多2小時，且有效時數不得太於實際開播時數，本日及昨日可以立即查詢', 'broadcaster2_token', 'broadcaster2_nonce', masterList[2], 2),
            ('直播主只能查詢自己的收益資料', 'broadcaster_token', 'broadcaster_nonce', masterList[1], 4)
        ]
    elif funName == 'receiveTotal':
        #scenario, token, nonce, masterId, periods, condition, items, expected
        testData = [  
            ('直播主查詢昨日收禮總計', 'broadcaster_token', 'broadcaster_nonce', masterList[0], [1, 2], '?item=10&page=1', 10, 2),
            ('直播主查詢本月收禮總計', 'broadcaster_token', 'broadcaster_nonce', masterList[0], [0, 2], '?item=10&page=1', 10, 2),
            ('直播主查詢本日收禮總計', 'broadcaster1_token', 'broadcaster1_nonce', masterList[1], [0, 1], '?item=10&page=1', 10, 2),
            ('直播主查詢本日收禮總計指定每頁顯示筆數', 'broadcaster1_token', 'broadcaster1_nonce', masterList[1], [0, 1], '?item=1&page=1', 1, 2),
            ('直播主無收禮資訊', 'broadcaster3_token', 'broadcaster3_nonce', masterList[3], [0, 1], '?item=10&page=1', 10, 2),
            ('直播主只能查詢自己的收禮總', 'broadcaster_token', 'broadcaster_nonce', masterList[1], [1, 2], '?item=10&page=1', 10, 4)
        ]
    elif funName == 'receiveDetail':
        testData = [  
            ('直播主查詢昨日收禮明細', 'broadcaster_token', 'broadcaster_nonce', masterList[0], [1, 2], '?item=10&page=1', 10, 2),
            ('直播主查詢本月收禮明細', 'broadcaster_token', 'broadcaster_nonce', masterList[0], [0, 2], '?item=10&page=1', 10, 2),
            ('直播主查詢本日收禮明細', 'broadcaster1_token', 'broadcaster1_nonce', masterList[1], [0, 1], '?item=10&page=1', 10, 2),
            ('直播主查詢本日收禮明細指定每頁顯示筆數', 'broadcaster1_token', 'broadcaster1_nonce', masterList[1], [0, 1], '?item=1&page=1', 1, 2),
            ('直播主無收禮資訊', 'broadcaster3_token', 'broadcaster3_nonce', masterList[3], [0, 1], '?item=10&page=1', 10, 2),
            ('直播主只能查詢自己的明細', 'broadcaster_token', 'broadcaster_nonce', masterList[1], [1, 2], '?item=10&page=1', 10, 4) 
        ]
    elif funName == 'sendDetail':
        testData = [  
            ('用戶查詢昨日收禮明細', 'user_token', 'user_nonce', userList[1], [1, 2], '?item=10&page=1', 10, 2),
            ('用戶查詢本月收禮明細', 'user_token', 'user_nonce', userList[1], [0, 2], '?item=10&page=1', 10, 2),
            ('用戶查詢本日收禮明細', 'user1_token', 'user1_nonce', userList[0], [0, 1], '?item=10&page=1', 10, 2),
            ('用戶查詢本日收禮明細指定每頁顯示筆數', 'user1_token', 'user1_nonce', userList[0], [0, 1], '?item=1&page=1', 1, 2),
            ('用戶只能查詢自己的明細', 'broadcaster_token', 'broadcaster_nonce', userList[1], [1, 2], '?item=10&page=1', 10, 4) 
        ]
    elif funName == 'backendConsumed':
        testData = [  
            ('查詢用戶昨日收禮明細', 'backend_token', 'backend_nonce', userList[1], [1, 2], '?item=10&page=1', 10, 2),
            ('查詢用戶本月收禮明細', 'backend_token', 'backend_nonce', userList[1], [0, 2], '?item=10&page=1', 10, 2),
            ('查詢用戶本日收禮明細', 'backend_token', 'backend_nonce', userList[0], [0, 1], '?item=10&page=1', 10, 2),
            ('查詢用戶本日收禮明細指定每頁顯示筆數', 'backend_token', 'backend_nonce', userList[0], [0, 1], '?item=1&page=1', 1, 2),
            ('只能admin查詢', 'user_token', 'user_nonce', userList[1], [1, 2], '?item=10&page=1', 10, 4) 
        ]
    elif funName == 'backendRevenue':
        testData = [  
            ('以id查詢昨日收禮明細', 'backend_token', 'backend_nonce', 'liveMasterId', [masterList[0], masterList[1], masterList[2], masterList[3]], [1, 2], '?item=10&page=1', 10, 2),
            ('以agencyid查詢本月收禮明細', 'backend_token', 'backend_nonce', 'agencyIds', ['1', '10'], [0, 3], '?item=10&page=1', 10, 2),
            ('以agencyid查詢本日收禮明細', 'backend_token', 'backend_nonce', 'agencyIds', ['1', '10'], [0, 1], '?item=10&page=1', 10, 2),
            ('以id本日收禮明細指定每頁顯示筆數', 'backend_token', 'backend_nonce', 'liveMasterId', [masterList[0], masterList[1]], [0, 1], '?item=1&page=1', 1, 2),
            ('只有admin能查詢明細', 'broadcaster_token', 'broadcaster_nonce', 'liveMasterId', [masterList[0], masterList[1]], [1, 2], '?item=10&page=1', 10, 4) 
        ]
    elif funName == 'backendHours': 
        testData = [  
            ('以id查詢昨日開播時間查詢', 'backend_token', 'backend_nonce', 'userIds', [masterList[0], masterList[1], masterList[2], masterList[3]], [1, 2], '?item=10&page=1', 10, 2),
            ('以agencyid查詢本月開播時數', 'backend_token', 'backend_nonce', 'agencyIds', ['1', '10'], [0, 3], '?item=10&page=1', 10, 2),
            ('以id本日開播時數指定每頁顯示筆數', 'backend_token', 'backend_nonce', 'userIds', [masterList[0], masterList[1], masterList[2], masterList[3]], [0, 1], '?item=1&page=1', 1, 2),
            ('只有admin能查詢明細', 'broadcaster_token', 'broadcaster_nonce', 'userIds', [masterList[0], masterList[1]], [1, 2], '?item=10&page=1', 10, 4) 
        ]
    elif funName == 'giftGiver':
        #排行榜官網會使用，不做token/nonce判斷
        testData = [
            ('以category作查詢條件', 'backend_token', 'backend_nonce', 'giftCategory', 108, [0, 2], 2),
            ('以giftid作查詢條件', 'broadcaster_token', 'broadcaster_nonce', 'giftId', '5976e63d-7166-4585-a3a3-fb48efed9a37', [0, 2], 2),
            ('以直播主作查詢條件', 'user_token', 'user_nonce', 'liveMasterId', ['d82a7ba2-5c11-4615-aba7-2a768d927165', '971f5a08-a8df-493a-93ca-8df6022963de'], [0, 2], 2),
            ('僅以giftType作為查詢條件', 'backend_token', 'backend_nonce', 'giftId', '1', [0, 2], 2),
            ('僅以時間作為查詢條件', 'backend_token', 'backend_nonce', None, None, [0, 2], 2),
            ('token/nonce不存在', 'err_token', 'err_nonce', 'giftCategory', 108, [0, 2], 2)
        ]
    elif funName == 'liveMaster':
        #排行榜官網會使用，不做token/nonce判斷
        testData = [
            ('以livemasterId做查詢', 'backend_token', 'backend_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], 2),
            ('以tagegroup作查詢條件', 'broadcaster_token', 'broadcaster_nonce', 'tagGroups', [5], [0, 2], 2),
            ('以tag作查詢條件', 'user_token', 'user_nonce', 'tags', [6, 8], [0, 2], 2),
            ('以性別作查詢條件', 'user_token', 'user_nonce', 'gender', 'female', [0, 2], 2),
            ('以性別作查詢條件', 'user_token', 'user_nonce', 'gender', 'male', [0, 2], 2),
            ('以性別作查詢條件', 'user_token', 'user_nonce', 'gender', 'all', [0, 2], 2),
            ('以orderBy作查詢條件', 'user_token', 'user_nonce', 'orderBy', 'hot', [0, 2], 2),
            ('以targetMonth作查詢條件', 'user_token', 'user_nonce', 'targetMonth', '', [0, 2], 2),
            ('僅以時間作為查詢條件', 'err_token', 'err_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], 2)
        ]    
    elif funName == 'bkliveMaster':
        testData = [
            ('以livemasterId做查詢', 'backend_token', 'backend_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], '?item=10&page=1', 2),
            ('以tagegroup作查詢條件', 'backend_token', 'backend_nonce', 'tagGroups', [5], [0, 2], '?item=10&page=1', 2),
            ('以tag作查詢條件', 'backend_token', 'backend_nonce', 'tags', [6, 8], [0, 2], '?item=10&page=1', 2),
            ('以性別作查詢條件', 'backend_token', 'backend_nonce', 'gender', 'female', [0, 2], '?item=10&page=1', 2),
            ('以性別作查詢條件', 'backend_token', 'backend_nonce', 'gender', 'male', [0, 2], '?item=10&page=1', 2),
            ('以性別作查詢條件', 'backend_token', 'backend_nonce', 'gender', 'all', [0, 2], '?item=10&page=1', 2),
            ('以giftType作查詢條件', 'backend_token', 'backend_nonce', 'giftType', '1', [0, 2], '?item=10&page=1', 2),
            ('以orderBy作查詢條件', 'backend_token', 'backend_nonce', 'orderBy', 'hot', [0, 2], '?item=10&page=1', 2),
            ('以targetMonth作查詢條件', 'backend_token', 'backend_nonce', 'targetMonth', '', [0, 2], '?item=10&page=1', 2),
            ('後台直播主排行榜權限僅供admin查詢。若broadcaster查詢則會錯', 'broadcaster_token', 'broadcaster_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], '?item=10&page=1', 4),
            ('後台直播主排行榜權限僅供admin查詢。若user查詢則會錯', 'user_token', 'user_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], '?item=10&page=1', 4),
            ('後台直播主排行榜未給token/nonce則會錯', 'err_token', 'err_nonce', 'liveMasterId', 'd82a7ba2-5c11-4615-aba7-2a768d927165', [0, 2], '?item=10&page=1', 4)
        ]    
    return testData
 
class TestMasterReport(): 
    @pytest.mark.parametrize("scenario, token, nonce, masterId, expected", getTestData('revenue'))
    def testRevenue(self, testInitial, scenario, token, nonce, masterId, expected):
        compareResult = {'today':{'points': 0, 'liveTimeSec':0}, 'yesterday':{'points': 0, 'liveTimeSec':0}, 'thisMonth':{'points': 0, 'liveTimeSec':0}}
        apiName = '/api/v2/liveMaster/' + masterId + '/revenue/summary'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]         
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {})
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            keyList = result[masterId].keys()
            for i in keyList:
                if i != 'info':
                    if str(i) == '0':
                        compareResult['today']['points'] += result[masterId][i]['points']['points']
                        compareResult['today']['liveTimeSec'] += min(result[masterId][i]['onAir']['active'], result[masterId][i]['onAir']['real'], result[masterId]['info']['max'])
                    elif str(i) == '1':
                        compareResult['yesterday']['points'] += result[masterId][i]['points']['points']
                        compareResult['yesterday']['liveTimeSec'] += min(result[masterId][i]['onAir']['active'], result[masterId][i]['onAir']['real'], result[masterId]['info']['max'])
                    compareResult['thisMonth']['points'] += result[masterId][i]['points']['points']
                    compareResult['thisMonth']['liveTimeSec'] += min(result[masterId][i]['onAir']['active'], result[masterId][i]['onAir']['real'], result[masterId]['info']['max'])
            pprint(compareResult)
            assert restext['today']['points'] == compareResult['today']['points']
            assert int(restext['today']['liveTimeSec']) == compareResult['today']['liveTimeSec']
            assert restext['yesterday']['points'] == compareResult['yesterday']['points'] 
            assert int(restext['yesterday']['liveTimeSec']) == compareResult['yesterday']['liveTimeSec']
            assert restext['thisMonth']['points'] == compareResult['thisMonth']['points']
            assert int(restext['thisMonth']['liveTimeSec']) == compareResult['thisMonth']['liveTimeSec']

    @pytest.mark.parametrize("scenario, token, nonce, masterId, periods, condition, items, expected", getTestData('receiveTotal'))
    def testGiftTotal(self, testInitial, scenario, token, nonce, masterId, periods, condition, items, expected):
        compareResult = {}
        for i in range(periods[0], periods[1]):
            if result[masterId].get(str(i)):
                for j in result[masterId][str(i)]['summary']:
                    sender = j.keys()
                    for k in sender:
                        if compareResult.get(k):
                            compareResult[k] += j[k]  
                        else:
                            compareResult[k] = j[k]  
        dict(sorted(compareResult.items(), key=lambda x: x[1])) 
        apiName = '/api/v2/liveMaster/' + masterId + '/receiveGift/total' + condition
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {'startTime': start_at, 'endTime': end_at})
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert restext['totalCount'] == len(compareResult)
            assert len(restext['data']) <= items
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['points'] <= restext['data'][i - 1]['points']
                restext['data'][i]['points'] = compareResult[restext['data'][i]['user']['id']]

    @pytest.mark.parametrize("scenario, token, nonce, masterId, periods, condition, items, expected", getTestData('receiveDetail'))
    def testGiftDetail(self, testInitial, scenario, token, nonce, masterId, periods, condition, items, expected):
        compareResult = []
        for i in range(periods[0], periods[1]):
            if result[masterId].get(str(i)):
                compareResult.extend(result[masterId][str(i)]['detail'])
        apiName = '/api/v2/liveMaster/' + masterId + '/receiveGift/detail' + condition
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {'startTime': start_at, 'endTime': end_at})
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) <= items
            assert restext['totalCount'] == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['createAt'] <= restext['data'][i - 1]['createAt']
                isFound = False
                for j in compareResult:
                    if all([any([j['create_at'] == restext['data'][i]['createAt'],j['points'] == restext['data'][i]['points']]), j['uid'] == restext['data'][i]['user']['id']]):
                        isFound = True
                        assert j['points'] == restext['data'][i]['points']
                        assert j['name'] == restext['data'][i]['giftName']
                        assert j['uid'] == restext['data'][i]['user']['id']
                        break
                assert isFound
        
    @pytest.mark.parametrize("scenario, token, nonce, userId, periods, condition, items, expected", getTestData('sendDetail'))
    def testSendDetail(self, testInitial, scenario, token, nonce, userId, periods, condition, items, expected):
        compareResult = []
        for i in range(periods[0], periods[1]):
            #pprint(result[userId])
            if result[userId].get(str(i)):
                if i > 0: 
                    compareResult.extend(result[userId][str(i)]['detail'], result[userId]['info']['agencyInfo'][1]['name'])
                else:
                    compareResult.extend(result[userId][str(i)]['detail'], result[userId]['info']['agencyInfo'][0]['name'])
        #pprint(compareResult)
        apiName = '/api/v2/identity/' + userId + '/sendGift/detail' + condition
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {'startTime': start_at, 'endTime': end_at})
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) <= items
            assert restext['totalCount'] == len(compareResult)
            assert len(restext['data']) == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['createAt'] <= restext['data'][i - 1]['createAt']
                isFound = False
                for j in compareResult:
                    if all([any([j['create_at'] == restext['data'][i]['createAt'],j['points'] == restext['data'][i]['giftPoint']]),j['liveMasterId'] == restext['data'][i]['user']['id']]):
                        isFound = True
                        assert j['points'] == restext['data'][i]['giftPoint']
                        assert j['name'] == restext['data'][i]['giftName']
                        assert j['liveMasterId'] == restext['data'][i]['user']['id']
                        break
                assert isFound

    def getBackendCompareData(self, beg, end, keys, values):
        compare = []
        for i in masterList:
            isAdd = False
            if keys == 'liveMasterId':
                isAdd = True if i in values else False
            else:
                for k in result[i]['info']['agencyInfo']:
                    if k in values:
                        isAdd = True
                        break
                    else:
                        isAdd = False
            if isAdd:
                for j in range(beg, end):
                    compareData = {}
                    createAt = int((datetime.strptime(((datetime.today() - timedelta(days=j + 1)).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
                    compareData['createAt'] = createAt
                    compareData['liveTimeSum']       = min(result[i][str(j)]['onAir']['active'], result[i][str(j)]['onAir']['real'], result[i]['info']['max'])
                    compareData['liveMasterLoginId'] = result[i]['info']['loginId']
                    compareData['liveroomPoints']    = result[i][str(j)]['points']['liveroomPoints']
                    compareData['liveshowPoints']    = result[i][str(j)]['points']['liveshowPoints']
                    compareData['postwallPoints']    = result[i][str(j)]['points']['postwallPoints']
                    compareData['imPoints']          = result[i][str(j)]['points']['imPoints']
                    compareData['gamePoints']        = result[i][str(j)]['points']['gamePoints']
                    compareData['points']            = result[i][str(j)]['points']['points']
                    compareData['nickname']          = result[i]['info']['nickname']
                    compare.append(compareData)
        return compare

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, condition, items, expected", getTestData('backendRevenue'))
    def testBackendRevenue(self, testInitial, scenario, token, nonce,  keys, values, periods, condition, items, expected):
        compareResult = self.getBackendCompareData(periods[0], periods[1], keys, values) 
        apiName = '/api/v2/backend/liveMaster/revenue/summary' + condition                                                                                                                                                                                                        
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        body =  {'startTime': start_at, 'endTime': end_at}
        body[keys] = values if keys else None
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) <= items
            assert restext['totalCount'] == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['createAt'] <= restext['data'][i - 1]['createAt']
                isFound = False
                for j in compareResult:
                    if all([j['createAt'] == restext['data'][i]['createAt'], j['liveMasterLoginId'] == restext['data'][i]['liveMasterLoginId'], j['nickname'] == restext['data'][i]['liveMasterNickname']]):
                        isFound = True
                        assert j['liveTimeSum']      == restext['data'][i]['liveTimeSum']
                        assert j['liveroomPoints']   == restext['data'][i]['liveroomPoints']
                        assert j['liveshowPoints']   == restext['data'][i]['liveshowPoints']
                        assert j['postwallPoints']   == restext['data'][i]['postwallPoints']
                        assert j['imPoints']         == restext['data'][i]['imPoints']
                        assert j['gamePoints']       == restext['data'][i]['gamePoints']
                        assert j['points']           == restext['data'][i]['points']
                        break
                assert isFound

    @pytest.mark.parametrize("scenario, token, nonce, userId, periods, condition, items, expected", getTestData('backendConsumed'))
    def testBackendConsumed(self, testInitial, scenario, token, nonce, userId, periods, condition, items, expected):
        compareResult = []
        for i in range(periods[0], periods[1]):
            if result[userId].get(str(i)):
                print('data count = ', len(result[userId][str(i)]['detail']))
                for j in result[userId][str(i)]['detail']:
                    tempDic = {}
                    tempDic = j.copy()
                    tempDic['agency'] = result[j['liveMasterId']]['info']['agencyInfo']['0']['name'] if i == 0 else result[j['liveMasterId']]['info']['agencyInfo']['1']['name']
                    compareResult.append(tempDic)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        condition = condition + '&startTime=' + str(start_at) + '&endTime=' + str(end_at)
        apiName = '/api/v2/backend/user/usageList/'+ userId + condition                                                                                                                                                                                                        
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        #pprint(compareResult)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) <= items
            assert restext['totalCount'] == len(compareResult)
            assert len(restext['data']) == min(restext['totalCount'], items)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['createAt'] <= restext['data'][i - 1]['createAt']
                isFound = False
                for j in compareResult:
                    if  all([j['historyId'] == 0, abs(j['create_at'] - restext['data'][i]['createAt']) <= 5]):            
                        assert j['points'] == restext['data'][i]['point']
                        assert j['liveMasterId'] == restext['data'][i]['liveMasterId']
                        assert j['name'] == restext['data'][i]['giftName']
                        assert j['agency'] == restext['data'][i]['agency']
                        isFound = True
                        break
                    elif all([j['historyId'] != 0, j['historyId'] == restext['data'][i]['historyId'], j['name'] == restext['data'][i]['giftName']]):
                        assert j['points'] == restext['data'][i]['point']
                        assert j['liveMasterId'] == restext['data'][i]['liveMasterId']
                        assert j['agency'] == restext['data'][i]['agency']
                        isFound = True
                        break
                assert isFound

    def getHoursData(self, beg, end, keys, values):
        checkList = []
        for i in masterList:
            isAdd = False
            if keys == 'userIds':
                isAdd = True if i in values else False
            else:
                for k in result[i]['info']['agencyInfo']:
                    if k in values:
                        isAdd = True
                        break
                    else:
                        isAdd = False
            if isAdd:
                compare = []
                for j in range(beg, end):
                    isAppend = False
                    if result[i].get(str(j)):
                        activeSec = min(result[i][str(j)]['onAir']['active'], result[i][str(j)]['onAir']['real'], result[i]['info']['max'])
                        compare.insert(0, format(round(activeSec/3600, 2), '0.2f'))
                        compare.insert(0, format(round(result[i][str(j)]['onAir']['real']/3600, 2), '0.2f'))
                        if all([result[i][str(j)]['onAir']['real'] > 0, isAppend == False]):
                            isAppend = True
                compare.insert(0, result[i]['info']['loginId'])
                compare.insert(0, result[i]['info']['nickname'])
                checkList.append(compare) if isAppend else None
        return checkList

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, condition, items, expected", getTestData('backendHours'))
    def testBackendDailyHours(self, testInitial, scenario, token, nonce,  keys, values, periods, condition, items, expected):
        compareResult = self.getHoursData(periods[0], periods[1], keys, values) 
        apiName = '/api/v2/backend/liveMaster/dailyHoursReport'                                                                                                                                                                                               
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        start_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[1])).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        end_at = int((datetime.strptime(((datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s'))
        body =  {'startDate': start_at, 'endDate': end_at}
        body[keys] = values if keys else None
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext) - len(compareResult) == 2, "資料筆數不一致"
            for i in range(1, len(restext) - 1):
                isFound = False
                for j in range(len(compareResult)):
                    if all([restext[i][0] == compareResult[j][0], restext[i][1] == compareResult[j][1]]):
                        isFound = True
                        for k in range(2, len(compareResult[j])):
                            assert restext[i][k] == str(compareResult[j][k])
                        break
                assert isFound, print(i)

    def giverCompare(self, beg, end, members, keys, values):
        compareResult = []    
        for k in members:
            compare = {
                'userId': '',
                'giftCount': 0,
                'points': 0
            }
            for i in range(beg, end):
                if keys == None:
                    if result[k].get(str(i)):
                        for g in result[k][str(i)]['detail']:
                            compare['giftCount'] += 1 if g['giftId'] != '' else 0
                        compare['points'] += result[k][str(i)]['points']
                        compare['userId'] = k
                else:
                    if result[k].get(str(i)):
                        for j in result[k][str(i)]['detail']:
                            #print(j)
                            isAdd = False
                            if type(values) == list:
                                isAdd = True if all([j[keys] != '', j[keys] in values]) else False
                            else:
                                isAdd = True if all([j[keys] != '', j[keys] == values]) else False
                            if isAdd:
                                compare['giftCount'] += 1 if j['giftId'] != '' else 0
                                compare['points'] += j['points']
                                compare['userId'] = k  
            compareResult.append(compare) if compare['points'] > 0 else None
        return compareResult

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, expected", getTestData('giftGiver'))
    def testGiftGiver(self, testInitial, scenario, token, nonce,  keys, values, periods, expected):
        compareResult = self.giverCompare(periods[0], periods[1], userList, keys, values)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]    
        apiName = '/api/v2/ranking/giftGiver'
        sTime = (datetime.today() - timedelta(days=periods[1] - 1)).strftime('%Y-%m-%d 00:00:00')
        eTime = (datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 23:59:59')
        body = {'startTime': sTime, 'endTime': eTime}
        body[keys] = values if keys != None else None
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['points'] <= restext['data'][i - 1]['points']
                isFound = False
                for j in compareResult:
                    if j['userId'] == restext['data'][i]['userId']:
                        assert j['points'] == restext['data'][i]['points']
                        assert j['giftCount'] == restext['data'][i]['giftCount']
                        assert len(restext['data'][i]['profilePicture']) > 0
                        isFound = True
                        break
                assert isFound

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, expected", getTestData('bkgiftGiver'))
    def testBackendGiftGiver(self, testInitial, scenario, token, nonce,  keys, values, periods, expected):
        compareResult = self.giverCompare(periods[0], periods[1], userList, keys, values)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]    
        apiName = '/api/v2/backend/ranking/giftGiver?item=20&page=1'
        sTime = (datetime.today() - timedelta(days=periods[1] - 1)).strftime('%Y-%m-%d 00:00:00')
        eTime = (datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 23:59:59')
        body = {'startTime': sTime, 'endTime': eTime}
        body[keys] = values if keys != None else None
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    restext['data'][i]['points'] <= restext['data'][i - 1]['points']
                isFound = False
                for j in compareResult:
                    if j['userId'] == restext['data'][i]['userId']:
                        assert j['points'] == restext['data'][i]['points']
                        assert j['giftCount'] == restext['data'][i]['giftCount']
                        assert len(restext['data'][i]['profilePicture']) > 0
                        isFound = True
                        break
                assert isFound

    def masterCompare(self, beg, end, members, keys, values):
        compareResult = []    
        for k in members:
            filterDic = {'liveMasterId': k, 'tagGroups':result[k]['info']['tagGroups'], 
                'gender':result[k]['info']['gender'], 'tags':result[k]['info']['tags']}
            compare = {'userId': '', 'giftCount': 0, 'points': 0, 'nickname': '', 'liveTimeSec':0}
            isAdd = False
            if any([keys =='orderBy', keys =='giftType', keys is None, all([keys == 'gender', values == 'all'])]):
                isAdd = True
            else :
                if type(values) == list:
                    if keys in ('tags', 'tagGroups'):
                        for i in filterDic[keys]:
                            if i in values:
                                isAdd = True 
                                break
                    else:
                        isAdd = True if all([filterDic.get(keys), filterDic[keys] in values]) else False   
                else:
                    isAdd = True if all([filterDic.get(keys), filterDic[keys] == values]) else False   
            if isAdd:
                for i in range(beg, end):                
                    if result[k].get(str(i)):
                        for g in result[k][str(i)]['detail']:
                            compare['giftCount'] += 1 if g['giftId'] != '' else 0
                        compare['points'] += result[k][str(i)]['points']['points']
                        compare['userId'] = k
                        compare['nickname'] = result[k]['info']['nickname']
                        compare['liveTimeSec'] += result[k][str(i)]['onAir']['hot']
            compareResult.append(compare) if compare['userId'] != '' else None
        pprint(compareResult)
        return compareResult

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, expected", getTestData('liveMaster'))
    def testLiveMaster(self, testInitial, scenario, token, nonce,  keys, values, periods, expected):
        compareResult = self.masterCompare(periods[0], periods[1], masterList, keys, values)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]    
        apiName = '/api/v2/ranking/liveMaster'
        sTime = (datetime.today() - timedelta(days=periods[1]-1)).strftime('%Y-%m-%d 00:00:00')
        eTime = (datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 23:59:59')
        body = {'startTime': sTime, 'endTime': eTime}
        if keys:
            if values:
                body[keys] = values
            else:
                body[keys] = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-01 00:00:00' 
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    if keys == 'orderBy':
                        assert restext['data'][i]['liveTimeSec'] <= restext['data'][i - 1]['liveTimeSec']
                    else:
                        assert restext['data'][i]['points'] <= restext['data'][i - 1]['points']
                isFound = False
                for j in compareResult:
                    if j['userId'] == restext['data'][i]['userId']:
                        assert j['points'] == restext['data'][i]['points']
                        assert j['giftCount'] == restext['data'][i]['giftCount']
                        assert j['liveTimeSec'] == restext['data'][i]['liveTimeSec']
                        assert restext['data'][i]['profilePicture'] not in (None, '')
                        assert restext['data'][i]['profileThumbPicture'] not in (None, '')
                        isFound = True
                        break
                assert isFound

    @pytest.mark.parametrize("scenario, token, nonce, keys, values, periods, condition, expected", getTestData('bkliveMaster'))
    def testBackendLiveMaster(self, testInitial, scenario, token, nonce,  keys, values, periods, condition, expected):
        compareResult = self.masterCompare(periods[0], periods[1], masterList, keys, values)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]    
        apiName = '/api/v2/backend/ranking/liveMaster' + condition
        sTime = (datetime.today() - timedelta(days=periods[1]-1)).strftime('%Y-%m-%d 00:00:00')
        eTime = (datetime.today() - timedelta(days=periods[0])).strftime('%Y-%m-%d 23:59:59')
        body = {'startTime': sTime, 'endTime': eTime}
        if keys:
            if values:
                body[keys] = values
            else:
                body[keys] = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-01 00:00:00' 
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert len(restext['data']) == len(compareResult)
            for i in range(len(restext['data'])):
                if i > 0:
                    if keys == 'orderBy':
                        assert restext['data'][i]['liveTimeSec'] <= restext['data'][i - 1]['liveTimeSec']
                    else:
                        assert restext['data'][i]['points'] <= restext['data'][i - 1]['points']
                isFound = False
                for j in compareResult:
                    if j['userId'] == restext['data'][i]['userId']:
                        assert j['points'] == restext['data'][i]['points']
                        assert j['giftCount'] == restext['data'][i]['giftCount']
                        assert j['liveTimeSec'] == restext['data'][i]['liveTimeSec']
                        assert restext['data'][i]['profilePicture'] not in (None, '')
                        assert restext['data'][i]['profileThumbPicture'] not in (None, '')
                        isFound = True
                        break
                assert isFound
