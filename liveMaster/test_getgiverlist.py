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
userList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

    
def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    for i in range(20):
        userAccount = 'track' + str(1500 + i)
        userList.append(api.search_user(test_parameter['prefix'], userAccount, header))
    initdata.resetData(test_parameter['db'], idList[2])
    #pprint(userList)


def teardown_module():
    pass


def sendGift(timeList, today, yesterday, thisWeek, thisMonth, lastMonth):
    sqlList = []
    giftList = ['07a0592e-5024-4f9a-82ec-d209cea5b7f6', 120000,  
                '253b4361-1b0d-499d-9943-4452ab81a88c', 100000,  
                '3a99582d-349e-42ca-b8d8-258b7e204566', 50000,  
                '4db5bbaa-fd4d-4fcd-a84d-6d84d99dc58a', 10000,
                '57cfc4a6-92f3-4c9f-86e5-045e3a5ba2fa', 2000000, #4
                '82bf8567-82e3-4e3a-b214-f543db589ed1', 70000,   
                '93364e78-6e3b-442d-9eca-d37d491666ef', 1200, 
                'a0974c79-b468-47b5-a1a4-7e8e3c3592f7', 30000,  
                'e6e8aed2-7571-4516-8376-78d1dd4031a0', 3000,   
                'ebb24748-0ff3-42a1-8e26-e809e2f5fadf', 5000,
                'fd514de8-fdfb-4c56-9170-a9d92ffa125a', 600000] #10
    for i in range(4):
        #print(timeList[i])
        sqlStr = "insert into live_room_gift(consumption_point, create_at, create_user_id, room_id, status, gift_id, target_user_id) values (" + str(giftList[i * 2 + 1])
        sqlStr += ", '" +  timeList[i] + "', '" + userList[i] + "', 5487, 0, '" + giftList[i * 2] + "', '" + idList[2] + "')"     
        sqlList.append(sqlStr)   
        print("i=%d, uid=%s, date=%s, point=%d"%(i, userList[i],  timeList[i % 4], giftList[i * 2 + 1]))
        if i == 0:
            if userList[i] in today:
                today[userList[i]] += giftList[i * 2 + 1]
            else:
                today[userList[i]] = giftList[i * 2 + 1]
            if userList[i + 1] in thisWeek:
                thisWeek[userList[i]] += giftList[i * 2 + 1]
            else:
                thisWeek[userList[i]] = giftList[i * 2 + 1]          
        if i == 1:
            if userList[i] in yesterday:
                yesterday[userList[i]] += giftList[i * 2 + 1]
            else:
                yesterday[userList[i]] = giftList[i * 2 + 1]  
            if datetime.today().weekday() < 6:
                if userList[i + 1] in thisWeek:
                    thisWeek[userList[i]] += giftList[i * 2 + 1]
                else:
                    thisWeek[userList[i]] = giftList[i * 2 + 1]          
        if i < 3:
            if userList[i + 1] in thisMonth:
                thisMonth[userList[i]] += giftList[i * 2 + 1]
            else:
                thisMonth[userList[i]] = giftList[i * 2 + 1]           
        else:
            if userList[i + 1] in lastMonth:
                lastMonth[userList[i]] += giftList[i * 2 + 1]
            else:
                lastMonth[userList[i]] = giftList[i * 2 + 1]           
    for i in range(4, 8):     
        #print(timeList[i%4])
        sqlStr = "insert into liveshow_gift_history(liveshow, team, giver_user_id, live_master_id, room_id, gift_id, points, ratio, create_at) values (1, 148, '"
        sqlStr += userList[i] + "', '" + idList[2] + "', 4567, '" + giftList[i * 2] + "'," + str(giftList[i * 2 + 1]) + ", 2.00, '" + timeList[i % 4] + "')"
        sqlList.append(sqlStr)   
        #print("i=%d, uid=%s, date=%s, point=%d"%(i, userList[i],  timeList[i % 4], giftList[i * 2 + 1]))
        if (i % 4) == 0:
            if userList[i] in today:
                today[userList[i]] += giftList[i * 2 + 1]
            else:
                today[userList[i]] = giftList[i * 2 + 1]
            if userList[i + 1] in thisWeek:
                thisWeek[userList[i]] += giftList[i * 2 + 1]
            else:
                thisWeek[userList[i]] = giftList[i * 2 + 1]          
        if (i % 4) == 1:
            #print("i=%d, userid=%s"%(i, userList[i]))
            if userList[i] in yesterday:
                yesterday[userList[i]] += giftList[i * 2 + 1]
            else:
                yesterday[userList[i]] = giftList[i * 2 + 1]  
            if datetime.today().weekday() < 6:
                if userList[i + 1] in thisWeek:
                    thisWeek[userList[i]] += giftList[i * 2 + 1]
                else:
                    thisWeek[userList[i]] = giftList[i * 2 + 1]          
        if (i % 4) < 3:
            if userList[i + 1] in thisMonth:
                thisMonth[userList[i]] += giftList[i * 2 + 1]
            else:
                thisMonth[userList[i]] = giftList[i * 2 + 1]           
        else:
            if userList[i + 1] in lastMonth:
                lastMonth[userList[i]] += giftList[i * 2 + 1]
            else:
                lastMonth[userList[i]] = giftList[i * 2 + 1]           
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    
def sendBarrage(timeList, today, yesterday, thisWeek, thisMonth, lastMonth):
    sqlList = []
    Barrage = [35, 350]
    for i in range(8, 10):
        ##print(timeList[i%8])
        sqlStr = "insert into live_room_gift(consumption_point, create_at, create_user_id, room_id, status, barrage_id, target_user_id) values (" + str(Barrage[i % 8])
        sqlStr += ", '" +  timeList[i % 8]  +"', '" + userList[i] + "', 5487, 0, '" + str(i % 8 + 1) + "', '" + idList[2] + "')"        
        sqlList.append(sqlStr)   
        print("i=%d, uid=%s, date=%s, point=%d"%(i, userList[i],  timeList[i % 8], Barrage[i % 8]))
        if (i % 8) == 0:
            if userList[i] in today:
                today[userList[i]] += Barrage[i % 8]
            else:
                today[userList[i]] = Barrage[i % 8]
            if userList[i] in thisWeek:
                thisWeek[userList[i]] += Barrage[i % 8]
            else:
                thisWeek[userList[i]] = Barrage[i % 8]         
        if (i % 8) == 1:
            if userList[i] in yesterday:
                yesterday[userList[i]] += Barrage[i % 8]
            else:
                yesterday[userList[i]] = Barrage[i % 8] 
            if datetime.today().weekday() < 6:
                if userList[i] in thisWeek:
                    thisWeek[userList[i]] += Barrage[i % 8]
                else:
                    thisWeek[userList[i]] = Barrage[i % 8]         
        if (i % 8) < 3:
            if userList[i] in thisMonth:
                thisMonth[userList[i]] += Barrage[i % 8]
            else:
                thisMonth[userList[i]] = Barrage[i % 8]          
        else:
            if userList[i] in lastMonth:
                lastMonth[userList[i]] += Barrage[i % 8]
            else:
                lastMonth[userList[i]] = Barrage[i % 8]         
    dbConnect.dbSetting(test_parameter['db'], sqlList)    

def createBody(valuesList):
    bodyDic = {}
    parameterList = ['receiver', 'origin', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']
    for i in range(len(valuesList)):
        bodyDic[parameterList[i]] = valuesList[i]
    return bodyDic

def sendMessage(original, repeats, timeList, today, yesterday, thisWeek, thisMonth, lastMonth):
    valuesList = []
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']  
    apiName = '/api/v2/liveMaster/instantMessage'
    content = '哈囉，你好。😄😄😄 ' 
    valuesList.extend([idList[0], original, 'text', content, '', '', ''])   
    body = createBody(valuesList)
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/identity/instantMessage'
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']  
    for i in range(repeats):
        valuesList.clear()
        content = '哈囉大主播，我是你的小粉1號;第' + str(i + 1) + '次傳訊息' 
        valuesList.extend([idList[2], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body) 
        #print(res.text) 
        if idList[0] in today:
            today[idList[0]] += 20
        else:
            today[idList[0]] = 20
        if idList[0] in thisMonth:
            thisMonth[idList[0]] += 20
        else:
            thisMonth[idList[0]] = 20
        if idList[0] in thisWeek:
            thisWeek[idList[0]] += 20
        else:
            thisWeek[idList[0]] = 20

class TestgetGiverList():
    today = {}
    yesterday = {}
    thisMonth = {}
    lastMonth = {}
    thisWeek = {}
    timeList = []
    def setup_class(self):
        sqlList = []
        for i in range(4):
            if i < 2:
                self.timeList.append((datetime.today() - timedelta(days=i) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))
            elif i == 2:   
                if datetime.today().weekday() == 0:                             
                    self.timeList.append((datetime.today() - timedelta(days=i) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    self.timeList.append((datetime.today() - timedelta(days=datetime.today().weekday()+i) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                self.timeList.append((datetime.today() - timedelta(days=datetime.today().day+i) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))
        #pprint(self.timeList)
        sendGift(self.timeList, self.today, self.yesterday, self.thisWeek, self.thisMonth, self.lastMonth)
        sendBarrage(self.timeList, self.today, self.yesterday, self.thisWeek, self.thisMonth, self.lastMonth)
        sqlList.append("update remain_points set remain_points = 100 where identity_id = '" + idList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        sendMessage('newUsersToSendIM', 3, self.timeList, self.today, self.yesterday, self.thisWeek, self.thisMonth, self.lastMonth)  

    def teardown_class(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        api.delete_block_user(test_parameter['prefix'], header, userList[0])
 
    def testGetTodayList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        stime = (datetime.today() - timedelta(hours=9))
        etime = (datetime.today() + timedelta(hours=1))
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(datetime.timestamp(etime))))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['totalCount'] == len(self.today)
        assert restext['sentCount'] == 0
        for i in restext['data']:
            i['user']['id'] in self.today
        assert restext['data'][0]['points'] >= restext['data'][1]['points']
    
    def testGetYesterdayList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        stime = (datetime.today() - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        etime = (datetime.today() - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(datetime.timestamp(etime))))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['totalCount'] == len(self.yesterday)
        assert restext['sentCount'] == 0
        for i in restext['data']:
            i['user']['id'] in self.yesterday
        assert restext['data'][0]['points'] >= restext['data'][1]['points']
    
    def testGetThisweekList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        dtweek = datetime.today().weekday()
        stime = (datetime.today() - timedelta(days=dtweek+1)).replace(hour=16, minute=0, second=0)
        etime = (datetime.today() + timedelta(days=6-dtweek)).replace(hour=15, minute=59, second=59)
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(datetime.timestamp(etime))))
        print(apiName)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['totalCount'] == len(self.thisWeek)
        assert restext['sentCount'] == 0
        for i in restext['data']:
            i['user']['id'] in self.thisWeek
        assert restext['data'][0]['points'] >= restext['data'][1]['points']
    
    def testGetThismonthList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        stime = (datetime.today() - timedelta(days=datetime.today().day-1)).replace(day=1, hour=0, minute=0, second=0)
        etime = (datetime.today() + timedelta(hours=1))
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(datetime.timestamp(etime))))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['totalCount'] == len(self.thisMonth)
        assert restext['sentCount'] == 0
        for i in restext['data']:
            i['user']['id'] in self.thisMonth
        assert restext['data'][0]['points'] >= restext['data'][1]['points']
    
    def testGetLastmonthList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        stime = (datetime.today() - timedelta(days=datetime.today().day)).replace(day=1, hour=0, minute=0, second=0)
        etime = (datetime.today() - timedelta(days=datetime.today().day)).replace(hour=15, minute=59, second=59)
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(datetime.timestamp(etime))))
        print(apiName)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['totalCount'] == len(self.lastMonth)
        assert restext['sentCount'] == 0
        for i in restext['data']:
            i['user']['id'] in self.lastMonth
        assert restext['data'][0]['points'] >= restext['data'][1]['points']
    
    def testUserInBlack(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        body = {'userId' : userList[0]}  
        api.add_block_user(test_parameter['prefix'], header, body)
        stime = (datetime.today()).replace(hour=0, minute=0, second=0)
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(time.time())))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert userList[0] not in restext['data']
    
    def testAuth(self):
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(time.time() - 600)))
        apiName = apiName.replace('{sTime}', str(int(time.time())))
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert res.status_code // 100 == 4

    def testWhitoutGiftList(self):
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']         
        stime = (datetime.today()).replace(hour=0, minute=0, second=0)
        apiName = '/api/v2/liveMaster/giftGiversToSendIM?startTime={sTime}&endTime={eTime}&item=10&page=1'
        apiName = apiName.replace('{sTime}', str(int(datetime.timestamp(stime))))
        apiName = apiName.replace('{eTime}', str(int(time.time())))
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0
        assert restext['sentCount'] == 0