import json
import requests
import time
import string
import random
import pytest
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
lmList = []
followList = {}
fansList = {}
create_At = int(time.time())
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
sTime = (datetime.fromtimestamp(int(time.time())) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

def getLivemasterList():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
    prefix = 'broadcaster0'
    for i in range(4):
        account = prefix + str(10 + i)
        lmList.append(api.search_user(test_parameter['prefix'], account, header))


def getFansList():
    sqlStr = "select login_id, token, nonce from identity where login_id between 'track0110' and 'track0124'"
    r = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    for i in r:
        fansList[i[0]] = [i[1], i[2]]
    #pprint(fansList)

def createLiveData(masterId, diffHours, diffMins,isSend):
    sqlList = []
    begDatetime = (datetime.fromtimestamp(int(time.time())) - timedelta(hours=diffHours) - timedelta(minutes=diffMins)).strftime('%Y-%m-%d %H:%M:%S')
    endDatetime = (datetime.fromtimestamp(int(time.time())) - timedelta(hours=diffHours)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
    sqlStr += masterId + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)" 
    sqlList.append(sqlStr)
    if isSend:
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
        sendID = api.search_user(test_parameter['prefix'], followList[masterId][0], header)
        sendDatetime = begDatetime = (datetime.fromtimestamp(int(time.time())) - timedelta(hours=diffHours) - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        sqlStr = "insert into live_room_gift set consumption_point = 35"
        sqlStr += ", create_at = '" + sendDatetime + "', "
        sqlStr += "create_user_id = '" + sendID + "', "
        sqlStr += "room_id = (select max(id) from live_room), status = 0, "
        sqlStr += "target_user_id = '" +  masterId + "', "
        sqlStr += "barrage_id = 1"       
    sqlList.append(sqlStr)
    dbConnect.dbSetting(test_parameter['db'], sqlList)

def setFollow():
    sqlList = []
    apiName = '/api/v2/identity/track'
    for i in range(len(fansList)):
        k = random.randrange(1, 12, 1)
        acc = 'track0' + str(110 + i)
        #print('acc=%s, token=%s, nonce=%s'%(acc, fansList[acc][0], fansList[acc][1]))
        for j in range(k % 4 + 1):
            if lmList[j] not in followList:
                followList[lmList[j]] = list()
            followList[lmList[j]].append(acc)
            header['X-Auth-Token'] = fansList[acc][0]
            header['X-Auth-Nonce'] = fansList[acc][1]
            body = {'liveMasterId': lmList[j]}
            #print(body)
            api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            #print(json.loads(res.text))
    sqlList.append("update fans_history set create_at = '" + str(sTime) + "'")
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    #pprint(followList)
    for i in range(2):
        createLiveData(lmList[i], i + 8, i * 10 + 30, True if i > 0 else False)

def initData():
    initdata.set_test_data(env, test_parameter)
    getLivemasterList()
    getFansList()
    initdata.resetData(test_parameter['db'], lmList[0])
    setFollow()

initData()

class TestFansRanking():
    broadcaster = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    def setup_class(self):
        result = api.user_login(test_parameter['prefix'], 'broadcaster010', '123456')
        self.broadcaster['X-Auth-Token'] = result['token']
        self.broadcaster['X-Auth-Nonce'] = result['nonce']

    def teardown_class(self):
        apiName = '/api/v2/liveMaster/blockUser/' +  followList[lmList[0]][0]
        api.apiFunction(test_parameter['prefix'], self.broadcaster, apiName, 'delete', None)

    def black(self):
        apiName = '/api/v2/liveMaster/blockUser'
        body = {'userId': followList[lmList[0]][0]}
        #print(body)
        api.apiFunction(test_parameter['prefix'], self.broadcaster, apiName, 'post', body)

    def cancelTracking(self):
        uid = followList[lmList[1]][0]
        apiName = '/api/v2/identity/track/' + lmList[1]
        header['X-Auth-Token'] = fansList[uid][0]
        header['X-Auth-Nonce'] = fansList[uid][1]
        api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        followList[lmList[1]].pop(0)

    @pytest.mark.parametrize("test_input, expected", [
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], 2),
        ([test_parameter['backend_token'], test_parameter['backend_nonce']], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce']], 2)
        #([test_parameter['err_token'], test_parameter['err_nonce']], 4)
    ])
    def testGetRanking(self, test_input, expected):
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        apiName = '/api/v2/ranking/liveMaster'
        eTime = datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
        body = {'orderBy': 'fans', 'startTime': sTime, 'endTime': eTime}
        #print(body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            for i in restext['data']:
                assert i['fansVariation'] == len(followList[i['userId']])

    def testBlackAndUnfollow(self):
        self.black()
        self.cancelTracking()
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
        apiName = '/api/v2/ranking/liveMaster'
        eTime = datetime.fromtimestamp(int(time.time()) + 1).strftime('%Y-%m-%d %H:%M:%S')
        body = {'orderBy': 'fans', 'startTime': sTime, 'endTime': eTime}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        for i in restext['data']:
            assert i['fansVariation'] == len(followList[i['userId']])
