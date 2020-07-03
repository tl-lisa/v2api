#milestone10：
    #新增v2追蹤及取消追蹤api（post/delete identity/track）#481 #482
    #取得追蹤中直播主動態列表（get identity/track/photoPost?item={{項數}}&page={{頁數}}）478
    #取得追蹤中且正在開播的直播主列表（get identity/track/liveMaster?filter=onAir&item={{項數}}&page={{頁數}}）
#milestone17
    #修改追蹤api。每次有追蹤或取消追蹤皆需新增資料到fans_history #792
#milestone20
    #重構所有相關api
    #新增可一次追蹤多名直播主(/v2/identity/multipleTrack) #977
#milestone25 針對photo加入type區別圖檔或影音檔
import json
import requests
import pymysql
import time
import string
import threading
import socket
import pytest
from assistence import chatlib
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from assistence import photo
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
liveMasterList = []

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'] , 
    [test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idList)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']  
    for i in range(10):
        liveMasterList.append(api.search_user(test_parameter['prefix'], 'broadcaster01' + str(i), header))
    liveMasterList.append('')

def getTestData(testType):
    testData = []
    if testType == 'singleTrack':
        # scenario, token, nonce, livemasterId, expected, totalCount
        testData = [
            ('happyCase', 'user_token', 'user_nonce', 0 , 2, 1),
            ('happyCase', 'user_token', 'user_nonce', 1, 2, 2),
            ('happyCase', 'broadcaster_token', 'broadcaster_nonce', 1, 2, 1),
            ('authNotFound', 'err_token', 'err_nonce', 1, 4, 0),
            ('livemasterIdNotFound', 'user_token', 'user_nonce', 3, 4, 2)
        ]
    elif testType == 'multipleTrack':
        #scenario, token, nonce, begin, end, expected, totalCount; Sam會判斷格式
        testData = [
            ('user1追蹤liveMasterList中的3位直播主', 'user1_token', 'user1_nonce', 2, 5, 2, 3),
            ('tl-lisa追蹤liveMasterList中的4位直播主', 'backend_token', 'backend_nonce', 3, 7, 2, 4),
            ('token/nonce不存在', 'err_token', 'err_nonce', 1, 5, 4, 0),
            ('帶入空的list', 'user1_token', 'user1_nonce', 1, 1, 2, 3),
            ('帶入字串而非list,應可會追蹤成功', 'user1_token', 'user1_nonce', 1, 0, 2, 4)
        ]
    elif testType == 'getTrackList':
        #scenario, action, token, nonce, expected, totalCount, begin, end, condition, items
        testData = [
            ('user同時追蹤二個直播主，追蹤清單應為2位直播主', '', 'user_token', 'user_nonce', 2, 2, 0, 2, '?item=10&page=1', 10),
            ('user同時追蹤二個直播主，指定開播中的直播主，應找出1位', 'onAir', 'user_token', 'user_nonce', 2, 1, 0, 1, '?filter=onAir&item=10&page=1', 10),
            ('user同時追蹤二個直播主，限制每頁僅顯示1筆資料', '', 'user_token', 'user_nonce', 2, 2, 0, 2, '?item=1&page=1', 1),
            ('broadcaster1將user列入黑名單，追蹤清單應為broadcaster', 'block', 'user_token', 'user_nonce', 2, 1, 0, 1, '?item=10&page=1', 10),
            ('broadcaster身份變成一般user，追蹤清單應為空的', 'changeRole', 'user_token', 'user_nonce', 2, 0, 0, 0, '?item=10&page=1', 10)
        ]
    elif testType == 'getPhoto':
        #scenario, action, token, nonce, expected, totalCount, begin, end, condition, items
        testData = [
            ('user同時追蹤二個直播主，應可取得2位直播主動態', '', 'user_token', 'user_nonce', 2, 4, 0, 2, '?item=10&page=1', 10),
            ('user同時追蹤二個直播主，但指定每頁的itme', '', 'user_token', 'user_nonce', 2, 4, 1, 2, '?item=2&page=1', 2),
            ('broadcaster1將user列入黑名單，應只能取得broadcaster的動態', 'block', 'user_token', 'user_nonce', 2, 2, 0, 1, '?item=10&page=1', 10),
            ('broadcaster身份變成一般user，應沒有任何一筆動態', 'changeRole', 'user_token', 'user_nonce', 2, 0, 0, 0, '?item=10&page=1', 10)
        ]
    elif testType == 'cancelTrack':
        #scenario, token, nonce, masterId, expected, totalCount
        testData = [
            ('happy case', 'user1_token', 'user1_nonce', 3, 2, 3),
            ('happy case', 'backend_token', 'backend_nonce', 3, 2, 3),
            ('authNotFound', 'err_token', 'err_nonce', 0, 4, 0),
            ('emptyId', 'user1_token', 'user1_nonce', -1, 4, 10),
            ('IdNotFound', 'user1_token', 'user1_nonce', 0, 4, 3),
        ]
    return testData


class TestTrack():
    def setup_class(self):
        initdata.clearFansInfo(test_parameter['db'])
    
    def checkDetail(self, header):
        urlName = '/api/v2/identity/track/liveMaster?item=10&page=1'  
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        return res.status_code, json.loads(res.text)

    @pytest.mark.parametrize("scenario, token, nonce, livemasterId, expected, totalCount", getTestData('singleTrack'))
    def testSingleTrack(self, scenario, token, nonce, livemasterId, expected, totalCount):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track'
        body = {"liveMasterId": idList[livemasterId]}
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            time.sleep(5)
            status, restext = self.checkDetail(header)
            assert status // 100 == 2
            assert restext['totalCount'] == totalCount

    @pytest.mark.parametrize("scenario, token, nonce, begin, end, expected, totalCount", getTestData('multipleTrack'))
    def testMultipleTrack(self, scenario, token, nonce, begin, end, expected, totalCount):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/multipleTrack'
        if end > 0:
            body = {"data": liveMasterList[begin:end]}  
        else: 
            body = {"data": liveMasterList[begin]}
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
        urlName = '/api/v2/identity/track/' + liveMasterList[masterId]
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'delete', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            time.sleep(5)
            status, restext = self.checkDetail(header)
            assert status // 100 == 2
            assert restext['totalCount'] == totalCount


@pytest.fixture(scope="class")
def testInit():
    createPhotoList = [
        ['photo', 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png', '動態照片上傳', '', '', '108'],
        ['', 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png', '動態照片上傳,未設type跟gift category', '', '', ''],
        ['video', '', '動態影片上傳', 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/096ee460b45c11eab2d142010a8c0017.png',
        'https://d3eq1e23ftm9f0.cloudfront.net/story/vedio/ef79cfbab45c11eab2d142010a8c0017.mp4', '108']
    ]
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    api.changeRole(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idList[0], idList[1]], 4)
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']  
    urlName = '/api/v2/identity/multipleTrack'
    body = {"data": [idList[0], idList[1]]}
    api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    array1 = ['broadcaster_token', 'broadcaster_nonce', 'broadcaster1_token', 'broadcaster1_nonce']  
    for i in range(2):
        for j in range(2):
            body = photo.createBody(*createPhotoList[j])
            photo.createPhoto(test_parameter[array1[i * 2]], test_parameter[array1[i * 2 + 1]], test_parameter['prefix'], body)
    time.sleep(5)

def Openroom(token, nonce, chat):
    header['X-Auth-Token'] = test_parameter[token]
    header['X-Auth-Nonce'] = test_parameter[nonce]  
    try: 
        apiName = '/api/v2/liveMaster/zego/liveRoom'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', {})
        restext = json.loads(res.text)
        if res.status_code == 200:
            roomId = restext['data']['roomId']
            sockinfo = api.get_load_balance(test_parameter['prefix'], header)
            sip = sockinfo['socketIp']
            sport = int(sockinfo['socketPort'])
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (sip, sport)
            sock.connect(server_address)
            chatlib.chat_room_auth(sock, header)  
            rid = chatlib.enterZego(sock, roomId)
            chat.extend([rid, sock])
        return
    except Exception as e:
        print(e)

class TestGetList():
    chat =[]
    def setup_class(self):
        changelist = [idList[0]] 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce'] 
        api.apiFunction(test_parameter['prefix'], header, '/api/v2/liveMaster/blockUser/' + idList[2] , 'delete', None) #清除黑名單
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']  
        urlName = '/api/v2/identity/multipleTrack'
        body = {"data": [idList[0], idList[1]]}
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)

    def teardown_class(self):
        chatlib.leave_room(self.chat[0], self.chat[1]) if self.chat != [] else None

    @pytest.mark.parametrize('scenario, action, token, nonce, expected, totalCount, begin, end, condition, items', getTestData('getTrackList'))
    def testGetTrackList(self, scenario, action, token, nonce, expected, totalCount, begin, end, condition, items):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], idList[2]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idList[0]], 5]},
            'onAir':{'funName':Openroom, 'parameter': ['broadcaster_token', 'broadcaster_nonce', self.chat]}
        }
        if action != '':
            actionDic[action]['funName'](*actionDic[action]['parameter'])
        time.sleep(30)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        urlName = '/api/v2/identity/track/liveMaster' + condition 
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        assert restext['totalCount'] == totalCount
        assert len(restext['data']) <= items
        for i in restext['data']:
            if action == 'onAir':
                assert i['onAir'] == True
            assert i['id'] in idList[begin:end]
            assert i['profilePicture'] != ''

    @pytest.mark.parametrize('scenario, action, token, nonce, expected, totalCount, begin, end, condition, items', getTestData('getPhoto'))
    def testGetPhotoList(self, testInit, scenario, action, token, nonce, expected, totalCount, begin, end, condition, items):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], idList[2]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idList[0]], 5]}
        }
        if action != '':
            actionDic[action]['funName'](*actionDic[action]['parameter'])
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]  
        time.sleep(30)
        urlName = '/api/v2/identity/track/photoPost' + condition #?item=10&page=1
        res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        assert restext['totalCount'] == totalCount
        assert len(restext['data']) <= items
        for i in restext['data']:
            assert i['owner']['profilePicture'] != ''
            assert i['giftCategoryId'] in (108, None)
            assert i['owner']['id'] in idList[begin:end]
            if i['type'] == 'video':
                assert all([i['videoPath'] != '', i['previewPath'] != ''], i['photoPath'] == i['previewPath'])
            else:
                assert all([i['photoPath'] != '', i['videoPath'] == '', i['photoPath'] == i['previewPath']])

