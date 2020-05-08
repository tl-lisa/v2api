#milestone10：
    #新增v2追蹤及取消追蹤api（post/delete identity/track）#481 #482
    #取得追蹤中直播主動態列表（get identity/track/photoPost?item={{項數}}&page={{頁數}}）478
    #取得追蹤中且正在開播的直播主列表（get identity/track/liveMaster?filter=onAir&item={{項數}}&page={{頁數}}）
#milestone17
    #修改追蹤api。每次有追蹤或取消追蹤皆需新增資料到fans_history #792
#milestone20
    #重構所有相關api
    #新增可一次追蹤多名直播主(/v2/identity/multipleTrack) #977
import json
import requests
import pymysql
import time
import string
import threading
import socket
import pytest
from ..assistence import chatlib
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import sundry
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
liveMasterList = []
initdata.set_test_data(env, test_parameter)
header['X-Auth-Token'] = test_parameter['backend_token']
header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))       
for i in range(10):
    liveMasterList.append(api.search_user(test_parameter['prefix'], 'broadcaster01' + str(i), header))

def getTestData(testType):
    testData = []
    if testType == 'singleTrack':
        # scenario, token, nonce, livemasterId, expected, totalCount
        testData = [
            ('happyCase', 'user_token', 'user_nonce', idList[0] , 2, 1),
            ('happyCase', 'user_token', 'user_nonce', idList[1], 2, 2),
            ('happyCase', 'broadcaster_token', 'broadcaster_nonce', idList[1], 2, 1),
            ('authNotFound', 'err_token', 'err_nonce', idList[1], 4, 0),
            ('livemasterIdNotFound', 'user_token', 'user_nonce', 'adfiou123', 4, 2)
        ]
    elif testType == 'multipleTrack':
        #scenario, token, nonce, livemasterList, expected, totalCount; Sam會判斷格式
        testData = [
            ('happy case', 'user1_token', 'user1_nonce', liveMasterList, 2, 10),
            ('happy case', 'backend_token', 'backend_nonce', liveMasterList, 2, 10),
            ('authNotFound', 'err_token', 'err_nonce', liveMasterList, 4, 0),
            ('emptyList', 'user1_token', 'user1_nonce', [], 2, 10),
            ('sendString', 'user1_token', 'user1_nonce', idList[1], 2, 10)
        ]
    elif testType == 'getList':
        #scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, livemasterlist
        testData = [
            ('user in Black', True, False, 'user_token', 'user_nonce', 2, 1, [idList[0]]),
            ('livemaster transform user', False, True, 'user_token', 'user_nonce', 2, 1, [idList[1]]),
            ('normal case', False, False, 'user_token', 'user_nonce', 2, 2, [idList[0], idList[1]])
        ]
    elif testType == 'getPhoto':
        #scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, livemasterlist
        testData = [
            ('user in Black', True, False, 'user_token', 'user_nonce', 2, 1, [idList[0]]),
            ('livemaster transform user', False, True, 'user_token', 'user_nonce', 2, 1, [idList[1]]),
            ('normal case', False, False, 'user_token', 'user_nonce', 2, 2, [idList[0], idList[1]])
        ]
    elif testType == 'cancelTrack':
        #scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, livemasterlist
        testData = [
            ('happy case', 'user1_token', 'user1_nonce', liveMasterList[0], 2, 9),
            ('happy case', 'backend_token', 'backend_nonce', liveMasterList[0], 2, 9),
            ('authNotFound', 'err_token', 'err_nonce', liveMasterList[0], 4, 0),
            ('emptyId', 'user1_token', 'user1_nonce', '', 4, 10),
            ('IdNotFound', 'user1_token', 'user1_nonce', 'usaoiejlaufeio', 4, 10),
        ]
    return testData


class TestTrack():
    def setup_class(self):
        initdata.clearFansInfo(test_parameter['db'])
    
    def checkDetail(self, eader):
        urlName = '/api/v2/identity/track/liveMaster?item=1&page=1'  
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        return res.status_code, json.loads(res.text)

    @pytest.mark.parametrize("scenario, token, nonce, livemasterId, expected, totalCount", getTestData('singleTrack'))
    def testSingleTrack(self, scenario, token, nonce, livemasterId, expected, totalCount):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track'
        body = {"liveMasterId": livemasterId}
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            time.sleep(5)
            status, restext = self.checkDetail(header)
            assert status // 100 == 2
            assert restext['totalCount'] == totalCount


    @pytest.mark.parametrize("scenario, token, nonce, liveMasterList, expected, totalCount", getTestData('multipleTrack'))
    def testMultipleTrack(self, scenario, token, nonce, liveMasterList, expected, totalCount):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/multipleTrack'
        body = {"data": liveMasterList}
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            time.sleep(5)
            status, restext = self.checkDetail(header)
            assert status// 100 == 2
            assert restext['totalCount'] == totalCount

    @pytest.mark.parametrize("scenario, token, nonce, masterId, expected, totalCount", getTestData('cancelTrack'))
    def testCancelTrack(self, scenario, token, nonce, masterId, expected, totalCount):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track/' + masterId
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'delete', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            time.sleep(5)
            status, restext = self.checkDetail(header)
            assert status // 100 == 2
            assert restext['totalCount'] == totalCount


@pytest.fixture(scope="class")
def testInit():
    initdata.clearFansInfo(test_parameter['db'])
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    url = '/api/v2/backend/user/role'
    body = {'ids': [idList[0], idList[1]], 'role': 4}
    api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)  
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']  
    urlName = '/api/v2/identity/multipleTrack'
    body = {"data": [idList[0], idList[1]]}
    api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    array1 = [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['broadcaster_acc'], 
            test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], test_parameter['broadcaster1_acc']]  
    for i in range(2):
        header['X-Auth-Token'] = array1[i * 3]
        header['X-Auth-Nonce'] = array1[i * 3 + 1]
        content = '我是' + array1[i * 3 + 2] + '的動態'
        body = {'photoPath': test_parameter['photo_url'],  'content': content} 
        api.add_photopost(test_parameter['prefix'], header, body)
        time.sleep(5)


class TestGetList():
    def setup_method(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
        url = '/api/v2/backend/user/role'
        body = {'ids': [idList[1]], 'role': 4}
        api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)  
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        api.delete_block_user(test_parameter['prefix'], header,  idList[2])

    @pytest.mark.parametrize('scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, masterId', getTestData('getList'))
    def testGetTrackList(self, testInit, scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, masterId):
        if isBlock:
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
            body = {'userId': idList[2]}
            api.add_block_user(test_parameter['prefix'], header, body)
        elif isChangeRole:
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
            url = '/api/v2/backend/user/role'
            body = {'ids': [idList[1]], 'role': 5}
            api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)  
        time.sleep(30)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track/liveMaster?item=10&page=1'  
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        assert restext['totalCount'] == totalCount
        for i in range(len(masterId)):
            if isBlock or isChangeRole:
                assert str(restext['data']).find(masterId[i]) < 0
            else:
                assert str(restext['data']).find(masterId[i]) >= 0
        for i in restext['data']:
            assert i['profilePicture'] != ''
        

    @pytest.mark.parametrize('scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, masterId', getTestData('getList'))
    def  testGetPhotoList(self, testInit, scenario, isBlock, isChangeRole, token, nonce, expected, totalCount, masterId):
        if isBlock:
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
            body = {'userId': idList[2]}
            api.add_block_user(test_parameter['prefix'], header, body)
        elif isChangeRole:
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
            url = '/api/v2/backend/user/role'
            body = {'ids': [idList[1]], 'role': 5}
            api.apiFunction(test_parameter['prefix'], header, url, 'patch', body)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        time.sleep(30)
        urlName = '/api/v2/identity/track/photoPost?item=10&page=1' 
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        assert restext['totalCount'] == totalCount
        for i in range(len(masterId)):
            if isBlock or isChangeRole:
                assert str(restext['data']).find(masterId[i]) < 0
            else:
                assert str(restext['data']).find(masterId[i]) >= 0
        for i in restext['data']:
            assert i['owner']['profilePicture'] != ''

def testOnair():
    header1 = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    apilink = '/api/v2/identity/track/liveMaster?filter=onAir&item=10&page=1'
    # 加入黑名單
    header1['X-Auth-Token'] = test_parameter['broadcaster_token']
    header1['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    body = {'userId': idList[3]}
    api.add_block_user(test_parameter['prefix'], header1, body)           
    sockinfo = api.get_load_balance(test_parameter['prefix'], header1)
    pprint(sockinfo)
    sip = sockinfo['socketIp']
    sport = int(sockinfo['socketPort'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (sip, sport)
    sock.connect(server_address)
    chatlib.chat_room_auth(sock, header1)
    rid = chatlib.new_room(sock, 'Test tracker 250行')
    while 1:        
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']           
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)        
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 1        
        assert restext['data'][0]['id'] == idList[0]
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        #assert len(restext['data']) == 0
        # 取消黑名單
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.delete_block_user(test_parameter['prefix'], header, idList[3])
        time.sleep(3)    
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0
        time.sleep(2)
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['id'] == idList[0]
        break
    chatlib.leave_room(rid, sock)           