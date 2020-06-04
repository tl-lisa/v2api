#milestone22 限定business_admin才可以操作
#完全相信後台的限制條件，後端不做任何資料檢查僅判權限
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import liveshowLib
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
liveMasterList = []
memberList = []

def getTestData(testType):
    testData = []
    if testType == 'create':
        #scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, expected
        testData = [
            ('create 1V1', 'backend_token', 'backend_nonce', 'TrueLove 1V1', 1, 3, 2, 1, 56, None, True, 2),
            ('create teams', 'backend_token', 'backend_nonce', 'TrueLove teams', 2, 3, 3, 3, 56, None, False, 2),
            ('create interview', 'backend_token', 'backend_nonce', 'TrueLove interview', 3, 3, 3, 3, 56, None, False, 2),
            ('create outsourcing', 'backend_token', 'backend_nonce', 'TrueLove outsourcing', 4, 1, 0, 0, 56, 
            'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False, 2),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 'TrueLove 1V1', 1, 3, 2, 1, 56, None, True, 4)
        ]
    elif testType == 'banner':
        #scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, isPrepare, expected
        testData = [
            ('create 1V1', 'backend_token', 'backend_nonce', 'TrueLove 1V1', 1, 3, 2, 1, 56, '', True, False, 'establish', 2),
            ('create teams', 'user_token', 'user_nonce', 'TrueLove teams', 2, 3, 3, 3, 56, '', False, False, 'prepare',2),
            ('create interview', 'liveController1_token', 'liveController1_nonce', 'TrueLove interview', 3, 3, 3, 3, 56, '', False, True, 'establish',2),
            ('create outsourcing', 'broadcaster_token', 'broadcaster_nonce', 'TrueLove outsourcing', 4, 1, 0, 0, 56, 
            'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False, False, 'prepare', 2),
            ('wrong auth', 'err_token', 'err_nonce', 'TrueLove 1V1', 1, 3, 2, 1, 56, '', True, False, 'establish', 4)
        ]
    elif testType == 'edit':
        #scenario, token, nonce, idIndex, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, showIndex, expected
        testData = [
            ('edit to teams', 'backend_token', 'backend_nonce', 1, 'TrueLove teams', 2, 2, 3, 3, 26, None, False, 1, 2),
            ('teams member change', 'backend_token', 'backend_nonce', 1, 'TrueLove teams', 2, 2, 3, 2, 56, None, False, 1, 2),
            ('teams and member number change', 'backend_token', 'backend_nonce', 1, 'TrueLove teams', 2, 2, 2, 3, 56, None, False, 1, 2),
            ('change to  interview', 'backend_token', 'backend_nonce', 1, 'TrueLove interview', 3, 1, 1, 1, 76, None, False, 1, 2),
            ('change to  1V1', 'backend_token', 'backend_nonce', 1, 'TrueLove 1V1', 1, 3, 2, 1, 56, None, True, 1, 2),
            ('change to  outsourcing', 'backend_token', 'backend_nonce', 1, 'TrueLove outsourcing', 4, 5, 0, 0, 56, 
            'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False, 1, 2),
            ('liveshow id is not found', 'backend_token', 'backend_nonce', 0, 'TrueLove teams', 3, 1, 1, 1, 76, None, False, 0, 4),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 1, 'TrueLove 1V1', 1, 3, 2, 1, 56, None, True, 1, 4)
        ]
    elif testType == 'del':
        #scenario, token, nonce, idIndex, isSend, expected
        #有送禮記錄的liveshow不可被刪，放在test_liveshowSendGift中驗證
        #是否可以刪除基本會在後台判斷。故不驗。
        testData = [
            ('happy case', 'backend_token', 'backend_nonce', 1, 2),
            ('liveshow id is not found', 'backend_token', 'backend_nonce', 0, 4),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 2, 4)
        ]
    elif testType == 'getbykey':
        #scenario, token, nonce, keyword, typeId, count, idList, expected
        testData = [
            ('query by title and type =all', 'backend_token', 'backend_nonce', 'TrueLove', 0, 4, [1, 2, 3, 4], 2),
            ('query by title and type =interview', 'backend_token', 'backend_nonce', 'interview', 3, 1, [2], 2),
            ('query by title and type =individual', 'backend_token', 'backend_nonce', 'TrueLove', 1, 1, [1], 2),
            ('query by title and type =outsourceing', 'backend_token', 'backend_nonce', 'TrueLove outsourcing', 4, 1, [4], 2),
            ('query by name and type =all', 'backend_token', 'backend_nonce', '5號', 0, 2, [2, 3], 2),
            ('key and type dismatch', 'backend_token', 'backend_nonce', 'TrueLove 1V1', 3, 0, [], 2), 
            ('key word not found', 'backend_token', 'backend_nonce', 'test', 0, 0, [], 2),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 'TrueLove', 9, 0, [], 4)
        ]
    elif testType == 'getbyid':
        #scenario, token, nonce, idIndex,  expected
        testData = [
            ('happy case', 'backend_token', 'backend_nonce', 1, 2),
            ('happy case', 'backend_token', 'backend_nonce', 4, 2),
            ('liveshow id is not found', 'backend_token', 'backend_nonce', 0, 4),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 2, 4)
        ]
    elif testType == 'prepare':
        #scenario, token, nonce, idIndex, isRepeat, expected
        testData = [
            ('happy case', 'backend_token', 'backend_nonce', 1,  False, 2),
            ('liveshow id is not found', 'backend_token', 'backend_nonce', 0,  False, 4),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 2,  False, 4),
            ('loveshow expired', 'backend_token', 'backend_nonce', 3,  False, 4),
            ('happy case', 'backend_token', 'backend_nonce', 2,  False, 2),
        ]
    elif testType == 'end':
        #與TPM討論end不設條件，愛怎麼end就怎麼end
        #scenario, token, nonce, idIndex, isPrepare, isRepeat, expected
        testData = [
            ('happy case', 'backend_token', 'backend_nonce', 'prepare', 2),
            ('not prepare', 'backend_token', 'backend_nonce', 'establish', 2),
            ('wrong auth', 'liveController1_token', 'liveController1_nonce', 'prepare', 4)
        ]
    return testData


def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearLiveshowData(test_parameter['db'])
    liveshowLib.createMember(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], memberList)

def compareResult(body, restext1, rtmpPullUrl):
    if restext1 == '':
        sqlStr = 'select id from liveshow where id = (select max(id) from liveshow)'
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        liveshowId = result[0][0]
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/backend/liveshow/' + str(liveshowId)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        # print('apiname=%s'%apiName)
        # pprint(body)
    else:
        sqlStr = "select id from liveshow where title = '" + body['title'] + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        liveshowId = result[0][0]
    #pprint(restext)
    if restext1 == '':
        assert restext['Status'] == 'Ok'
        assert restext['Message'] == 'SUCCESS'
        assert restext['data']['id'] == liveshowId
        assert restext['data']['title'] == body['title']
        assert restext['data']['bannerUrl'] == body['bannerUrl']
        assert restext['data']['bannerClickUrl'] == body['bannerClickUrl']
        assert restext['data']['liveBannerUrl'] == body['liveBannerUrl']
        assert restext['data']['bannerStartTime'] == body['bannerStartTime']
        assert restext['data']['bannerEndTime'] == body['bannerEndTime']
        assert restext['data']['liveStartTime'] == body['liveStartTime']
        assert restext['data']['liveEndTime'] == body['liveEndTime']
        assert restext['data']['type'] == body['type']
        assert restext['data']['poolId']['id'] == body['poolId']
        assert restext['data']['giftCategory'] == body['giftCategory']
        teamsKey = (restext['data']['teams']).keys()
        for i in teamsKey:
            for k in restext['data']['teams'][i]['members']:
                assert len(restext['data']['teams'][i]['members']) == len(body['teams'][i]['members'])
                isFind = False
                for j in body['teams'][i]['members']:
                    if k['id'] == j['id']:     
                        isFind = True   
                        sqlStr = "select login_id from identity where id = '" + k['id'] + "'"
                        record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                        assert k['nickname'] == j['nickname']
                        assert k['loginId'] == record[0][0]
                        assert 'thumbnail' in k
                        break
                assert isFind == True
            assert restext['data']['teams'][i]['name'] == body['teams'][i]['name']
        assert restext['data']['rtmpPullUrl'] == body['rtmpPullUrl']
        assert restext['data']['rtmpPushUrl'] != ''
    else:
        assert restext1['Status'] == 'Ok'
        assert restext1['Message'] == 'SUCCESS'
        for q in restext1['data']:
            assert q['id'] == liveshowId
            assert q['title'] == body['title']
            assert q['bannerUrl'] == body['bannerUrl']
            assert q['bannerClickUrl'] == body['bannerClickUrl']
            assert q['liveBannerUrl'] == body['liveBannerUrl']
            assert q['bannerStartTime'] == body['bannerStartTime']
            assert q['bannerEndTime'] == body['bannerEndTime']
            assert q['liveStartTime'] == body['liveStartTime']
            assert q['liveEndTime'] == body['liveEndTime']
            assert q['type'] == body['type']
            assert q['poolId']['id'] == body['poolId']
            assert q['giftCategory'] == body['giftCategory']
            teamsKey = (q['teams']).keys()
            for i in teamsKey:
                for k in q['teams'][i]['members']:
                    assert len(q['teams'][i]['members']) == len(body['teams'][i]['members'])
                    isFind = False
                    for j in body['teams'][i]['members']:
                        if k['id'] == j['id']:     
                            isFind = True   
                            sqlStr = "select login_id from identity where id = '" + k['id'] + "'"
                            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                            assert k['nickname'] == j['nickname']
                            assert k['loginId'] == record[0][0]
                            assert 'thumbnail' in k
                            break
                    assert isFind == True
                assert q['teams'][i]['name'] == body['teams'][i]['name']
            assert q['rtmpPullUrl'] == body['rtmpPullUrl']
            assert q['rtmpPushUrl'] != ''


def getLiveshowId(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty):
    apiName = '/api/v2/backend/liveshow/establish'
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    body = liveshowLib.createLiveshowBody(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, False, memberList)
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    sqlStr = 'select liveshow_id, id from liveshow where id = (select max(id) from liveshow)'
    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
    return result[0][0]

class TestCreateLiveshow():
    @pytest.mark.parametrize('scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, expected', getTestData('create'))
    def testEstablish(self, scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, expected):
        apiName = '/api/v2/backend/liveshow/establish'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        body = liveshowLib.createLiveshowBody(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, False, memberList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            compareResult(body, '', rtmpPullUrl)

class TestEditLiveshow():
    liveshowid = [999]   
    def setup_class(self):
        initdata.clearLiveshowData(test_parameter['db'])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        liveshowLib.establish(test_parameter['prefix'], test_parameter['db'], header, 'TrueLove 1V1', 1, 3, 2, 1, 56, None, True, False, memberList, self.liveshowid)

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, showIndex, expected', getTestData('edit'))
    def testPatchData(self, scenario, token, nonce, idIndex, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, showIndex, expected):
        apiName = '/api/v2/backend/liveshow/establish/' + str(self.liveshowid[showIndex])
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        body = liveshowLib.createLiveshowBody(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, False, memberList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'patch', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            compareResult(body, '', rtmpPullUrl)

class TestGetLiveshow():
    liveshowid = [0]   
    liveshowData = [['TrueLove 1V1', 1, 3, 2, 1, 36, None, True], ['TrueLove interview', 3, 3, 3, 3, 56, None, False], [ 'TrueLove teams', 2, 2, 3, 3, 76, None, False],
        ['TrueLove outsourcing', 4, 5, 0, 0, 1, 'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False]]
    bodyInfo = []
    def setup_class(self):
        initdata.clearLiveshowData(test_parameter['db'])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        for i in self.liveshowData:
            data = liveshowLib.establish(test_parameter['prefix'], test_parameter['db'], header, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], False, memberList, self.liveshowid)
            self.bodyInfo.append(data)
            time.sleep(1)
       
    @pytest.mark.parametrize('scenario, token, nonce, idIndex,  expected', getTestData('getbyid'))   
    def testGetDataByLoveshowId(self, scenario, token, nonce, idIndex, expected):
        apiName = '/api/v2/backend/liveshow/' + str(self.liveshowid[idIndex])
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok'
            assert restext['Message'] == 'SUCCESS'
            assert restext['data']['id'] == self.liveshowid[idIndex]
            assert restext['data']['title'] == self.liveshowData[idIndex - 1][0]
            assert restext['data']['type'] == self.liveshowData[idIndex - 1][1]
            assert restext['data']['rtmpPullUrl'] == self.liveshowData[idIndex - 1][6]
            assert restext['data']['giftCategory'] == self.liveshowData[idIndex - 1][5]
    
    @pytest.mark.parametrize('scenario, token, nonce, keyword, typeId, count, idList, expected', getTestData('getbykey'))   
    def testGetDataByKeyword(self, scenario, token, nonce, keyword, typeId, count, idList, expected):
        apiName = '/api/v2/backend/liveshow/list'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]   
        body = {
            "keyword": keyword,
            "type": typeId
        }
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok'
            assert restext['Message'] == 'SUCCESS'
            assert restext['totalCount'] == count
            if count > 0:
                if count == 1:
                    assert restext['data'][0]['id'] == self.liveshowid[idList[0]]
                    compareResult(self.bodyInfo[idList[0] - 1], restext, self.liveshowData[idList[0] - 1][6])
                else:
                    assert restext['data'][0]['id'] > restext['data'][1]['id']
            
    
class TestDelLiveshow():
    liveshowid = [0]   
    liveshowData = [['TrueLove 1V1', 1, 3, 2, 1, 36, None, True], ['TrueLove interview', 3, 3, 3, 3, 56, None, False], [ 'TrueLove teams', 2, 2, 3, 3, 76, None, False],
        ['TrueLove outsourcing', 4, 5, 0, 0, 1, 'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False]]
    def setup_class(self):
        initdata.clearLiveshowData(test_parameter['db'])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        for i in self.liveshowData:
            liveshowLib.establish(test_parameter['prefix'], test_parameter['db'], header, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], False, memberList, self.liveshowid)
            time.sleep(1)

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, expected', getTestData('del'))
    def testDeleteData(self, scenario, token, nonce, idIndex, expected):
        apiName = '/api/v2/backend/liveshow/' + str(self.liveshowid[idIndex])
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            sqlStr = "select delete_at from liveshow where id = " + str(self.liveshowid[idIndex])
            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            assert record[0][0] != None

class TestPrepareLiveshow():
    liveshowid = [0]   
    #title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired
    liveshowData = [
        ['TrueLove 1V1', 1, 1, 2, 1, 36, None, True, False], 
        ['TrueLove outsourcing', 4, 5, 0, 0, 0, 'https://www.youtube.com/watch?v=tFYkM-HbYN8&list=PLrM1U1vgxf6dfoPBQcV8uq_bQjMVLZ0A5&index=7', False, False],
        ['TrueLove interview', 3, 3, 3, 3, 56, None, False, True],
        ['TrueLove teamToteam', 2, 2, 2, 2, 36, None, True, False],
    ]
    def setup_class(self):
        initdata.clearLiveshowData(test_parameter['db'])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        for i in self.liveshowData:
            liveshowLib.establish(test_parameter['prefix'], test_parameter['db'], header, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], memberList, self.liveshowid)

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, isRepeat, expected',  getTestData('prepare'))
    def testPrepare(self, scenario, token, nonce, idIndex, isRepeat, expected):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/liveshow/prepare'
        body = {'liveshowId': self.liveshowid[idIndex]}
        #print(body)
        if isRepeat:
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            res1 = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            assert (res.status_code // 100 == 2 and res1.status_code // 100 == 4) or (res.status_code // 100 == 4 and res1.status_code // 100 == 2)
        else:
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            print(json.loads(res.text))
            assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['Message'] == 'SUCCESS'
            assert restext['Status'] == 'Ok'


class TestBanner():
    typeList = ['individual', 'team', 'interview', 'outsourcing']
    def setup_method(self):
        initdata.clearLiveshowData(test_parameter['db'])

    @pytest.mark.parametrize('scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, action, expected', getTestData('banner'))
    def testGetBanner(self, scenario, token, nonce, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, action, expected):
        liveshowId = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        funDic = {
            'prepare':  liveshowLib.liveshowPrepare,
            'establish': liveshowLib.establish
        }
        body = funDic[action](test_parameter['prefix'], test_parameter['db'], header,  title, liveshowType, poolId, teams_num, mumber_num, 
                            giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList, liveshowId)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/liveshow/banner'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok' 
            assert restext['Message'] == 'SUCCESS'
            for i in restext['data']:
                assert i['id'] == liveshowId[0]
                assert i['type'] == self.typeList[body['type'] - 1]
                assert i['bannerUrl'] == body['bannerUrl']
                assert i['bannerClickUrl'] == body['bannerClickUrl']
                assert i['liveBannerUrl'] == body['liveBannerUrl']
                if any([ action == 'establish', body['type'] == 4]):
                    assert i['rtmpPullUrl'] == body['rtmpPullUrl']
                else:
                    assert i['rtmpPullUrl'] != ''
                assert i['bannerStartTime'] == body['bannerStartTime']
                assert i['bannerEndTime'] == body['bannerEndTime']
                assert i['liveStartTime'] == body['liveStartTime']
                assert i['liveEndTime'] == body['liveEndTime']
                assert i['serverTimestamp'] <= int(time.time())

class TestLiveshowEnd():
    #title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired
    liveshowData = ['TrueLove 1V1', 1, 1, 2, 1, 36, None, True, False]
    def setup_method(self):
        initdata.clearLiveshowData(test_parameter['db'])

    #scenario, token, nonce, isPrepare, isRepeat, expected
    @pytest.mark.parametrize('scenario, token, nonce, action, expected', getTestData('end'))
    def testEnd(self, scenario, token, nonce, action, expected):
        liveshowId = []
        funDic = {
            'prepare':  liveshowLib.liveshowPrepare,
            'establish': liveshowLib.establish
        }
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        funDic[action](test_parameter['prefix'], test_parameter['db'], header,  self.liveshowData[0], self.liveshowData[1], 
            self.liveshowData[2], self.liveshowData[3], self.liveshowData[4], self.liveshowData[5], self.liveshowData[6], self.liveshowData[7], 
            self.liveshowData[8], memberList, liveshowId)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/backend/liveshow/end'
        body = {'liveshowId': liveshowId[0]}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext ['Status'] == 'Ok'
            assert restext ['Message'] == 'SUCCESS'

