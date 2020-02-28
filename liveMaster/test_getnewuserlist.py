import time
import json
import datetime
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
idList = []
liveList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}


def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], 'track0900', header))
    idList.append(api.search_user(test_parameter['prefix'], 'track0901', header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    initdata.resetData(test_parameter['db'], idList[0])
    for i in range(10):
        liveAccount = 'broadcaster0' + str(30 + i)
        liveList.append(api.search_user(test_parameter['prefix'], liveAccount, header))


def teardown_module():
    pass


class TestNewUserList():
    newlist = []
    def setup_class(self):
        sqlList = [] 
        experience = 11662       
        dtDay = (datetime.today() - timedelta(days=8+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        sqlStr1 = "update identity set create_at = '" + dtDay + "' where id in ('"
        for i in range (len(idList)):
            sqlStr = "update user_experience set experience = " + str(experience + i * 4500) +  " where identity_id = '" + idList[i] + "'"  
            sqlList.append(sqlStr)
            if len(idList) - i == 1:
                sqlStr1 += idList[i] + "')"
            else:
                sqlStr1 += idList[i] + "', '"
            if i < 4:
                self.newlist.append(idList[i])
        sqlList.append(sqlStr1)
        sqlStr = "update user_experience set experience = 42000 where identity_id in ('"           
        for i in range (len(liveList)):
            if len(liveList) - i == 1:
                sqlStr += liveList[i] + "')"
            else:
                sqlStr += liveList[i] + "', '"
        sqlList.append(sqlStr)    
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def createBody(self, valuesList):
        bodyDic = {}
        parameterList = ['receiver', 'origin', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']
        for i in range (len(valuesList)):
            bodyDic[parameterList[i]] = valuesList[i]
        return bodyDic

    def sendMessage(self, uid, orignal):
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        content = '哈囉，你好。😄😄😄 ' 
        valuesList.extend([uid, orignal, 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    
    def testCreateAtbeforLastWeekend(self):
        # 用戶註冊時間為上上周六23：59：59
        sqlList = []
        dtDay = datetime.today() - timedelta(days=9+datetime.today().weekday())
        dtDay = (dtDay.replace(hour=15, minute=59, second=59)).strftime('%Y-%m-%d %H:%M:%S')
        sqlList.append("update identity set create_at = '" + dtDay + "' where id = '" + idList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if idList[0] in self.newlist:
            self.newlist.remove(idList[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0
        assert restext['data'][0]['userLevel']['levelNum'] >= restext['data'][1]['userLevel']['levelNum']
    
    def testCreateAtLastSunday(self):
        # 用戶註冊時間為上周日00：00：00
        sqlList = []   
        dtDay = datetime.today() - timedelta(days=9+datetime.today().weekday())
        dtDay = (dtDay.replace(hour=16, minute=0, second=0)).strftime('%Y-%m-%d %H:%M:%S')
        sqlList.append("update identity set create_at = '" + dtDay + "' where id = '" + idList[0] + "'")
        print(sqlList[0])
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if idList[0] not in self.newlist:
            self.newlist.append(idList[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        #pprint(restext)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0

    def testCreateAtSunday(self):
        # 用戶註冊時間為週日00：00：00
        sqlList = []
        dtDay = datetime.today() - timedelta(days=2+datetime.today().weekday())
        dtDay = (dtDay.replace(hour=16, minute=0, second=0)).strftime('%Y-%m-%d %H:%M:%S')
        sqlStr = "update identity set create_at = '" + dtDay + "' where id = '" + idList[0] + "'"
        sqlList.append(sqlStr)
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if idList[0] in self.newlist:
            self.newlist.remove(idList[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0
    
    def testCreateAtLastSaturday(self):
        # 用戶註冊時間為上週六23：59：59
        sqlList = []
        dtDay = datetime.today() - timedelta(days=2+datetime.today().weekday())
        dtDay = (dtDay.replace(hour=15, minute=59, second=59)).strftime('%Y-%m-%d %H:%M:%S')
        sqlStr = "update identity set create_at = '" + dtDay + "' where id = '" + idList[0] + "'"
        sqlList.append(sqlStr)
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if idList[0] not in self.newlist:
            self.newlist.append(idList[0])
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        #pprint(restext)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0

    def testUserIsLiveMaster(self):
        # 新註冊用戶是直播主
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']         
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0

    def testUserLevelOver10(self):
        # 用戶等級大於青銅10
        sqlList = []
        sqlList.append("update user_experience set experience = experience + 15000 where identity_id = '" + idList[3] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if idList[3] in self.newlist:
            self.newlist.remove(idList[3])
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0
        sqlList.clear()
        sqlList.append("update user_experience set experience = experience - 15000 where identity_id = '" + idList[3] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        self.newlist.append(idList[3])

    def testUserInBlack(self):
        # 用戶在A直播主黑名單內；但不在B直播主名單內
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        body = {'userId' : idList[0]}  
        api.add_block_user(test_parameter['prefix'], header, body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        if idList[0] in self.newlist:
            self.newlist.remove(idList[0])
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0
        api.delete_block_user(test_parameter['prefix'], header, idList[0])
        self.newlist.append(idList[0])
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']    
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 0

    def testAlreadySendMessage(self):
        # 已送過訊息給該用戶;但其他直播主可以撈出
        getList = []
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        self.sendMessage(idList[0], 'newUsersToSendIM')     
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        if idList[0] in self.newlist:
            self.newlist.remove(idList[0])
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 1
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']    
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            getList.append(i['id'])
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist) + 1
        assert restext['sentCount'] == 0
        assert idList[0] in getList        

    def testSendMessageforGift(self):
        # 不計送禮訊息的次數，但名單不會被撈出
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        self.sendMessage(idList[1], 'giftGiversToSendIM')     
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        if idList[1] in self.newlist:
            self.newlist.remove(idList[1])
        print(idList[1])
        pprint(restext)
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 1
    
    def testReceive10Message(self):
        # 用戶已收到10個訊息即不會再被挑選出
        for i in range (12):
            liveAccount = 'broadcaster0' + str(30 + i)
            result = api.user_login(test_parameter['prefix'], liveAccount, test_parameter['user_pass'])
            header['X-Auth-Token'] = result['token']
            header['X-Auth-Nonce'] = result['nonce']
            self.sendMessage(idList[2], 'newUsersToSendIM')     
        if idList[2] in self.newlist:
            self.newlist.remove(idList[2])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code // 100 == 2
        for i in restext['data']:
            assert i['id'] in self.newlist
        assert restext['totalCount'] == len(self.newlist)
        assert restext['sentCount'] == 1

    def testWithouAuth(self):
        # 非直播主查詢
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
        apiName = '/api/v2/liveMaster/newUsersToSendIM'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == 4
    