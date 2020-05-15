#milestone18 加入動態贈禮
import time
import json
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta
from operator import itemgetter, attrgetter

env = 'QA'
test_parameter = {}
cards = []
idlist = []   
todayList = []
today1List = []
yesterdayList = []
lastmonthList = []
UserInfo = {}
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
rtmp_url = 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605'


def initTestingData():
    #print('init data')   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster2_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])

initdata.set_test_data(env, test_parameter) 
initTestingData()


def createHistoryData(startDate, dictype):
    sqlList = []
    data1 = [{'start_at': ' 01:30:00',
    'end_at': ' 01:40:00',
    'send_at': ' 01:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 11:20:00',
    'end_at': ' 11:50:00',
    'send_at': ' 11:31:00',
    'point': 35,
    'giftid': '',
    'barrageid': 1},
    {'start_at': ' 13:20:00',
    'end_at': ' 14:15:00',
    'send_at': ' 13:21:00',
    'point': 0,
    'giftid': '',
    'barrageid': 'NULL'},
    {'start_at': ' 15:50:00',
    'end_at': ' 16:31:00',
    'send_at': ' 16:01:00',
    'point': 3000,
    'giftid': 'e6e8aed2-7571-4516-8376-78d1dd4031a0',
    'barrageid': 'NULL'}]

    for i in range(len(data1)):
        begDatetime = startDate + data1[i]['start_at']
        endDatetime = startDate + data1[i]['end_at']
        sendDatetime = startDate + data1[i]['send_at']
        if data1[i]['giftid'] != '':
            sqlStr = "select name from gift_v2 where uuid = '" + data1[i]['giftid'] + "'"
            result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        if dictype == 'yesterday':
            if (data1[i]['send_at'] == ' 16:01:00'):
                if (data1[i]['giftid'] != '') and (data1[i]['point'] != 0):
                    todayList.append({'name': result[0][0], 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))}) 
                elif (data1[i]['giftid'] == '') and (data1[i]['point'] != 0):
                    todayList.append({'name': str(data1[i]['point']) + '點彈幕', 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
                else:
                    sqlStr = "select name, point from gift_v2 where uuid = '09875a92-8ab3-44bc-a83f-f9da6d5b6619'"
                    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                    todayList.append({'name': result[0][0], 'point': result[0][1], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
            else:
                #print('yeserter')
                if (data1[i]['giftid'] != '') and (data1[i]['point'] != 0):
                    yesterdayList.append({'name': result[0][0], 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
                elif (data1[i]['giftid'] == '') and (data1[i]['point'] != 0):
                    yesterdayList.append({'name': str(data1[i]['point']) + '點彈幕', 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
                else:
                    sqlStr = "select name, point from gift_v2 where uuid = '09875a92-8ab3-44bc-a83f-f9da6d5b6619'"
                    result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                    yesterdayList.append({'name': result[0][0], 'point': result[0][1], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
        else:  
            if (data1[i]['giftid'] != '') and (data1[i]['point'] != 0):
                lastmonthList.append({'name': result[0][0], 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
            elif (data1[i]['giftid'] == '') and (data1[i]['point'] != 0):
                lastmonthList.append({'name': str(data1[i]['point']) + '點彈幕', 'point': data1[i]['point'], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))}) 
            else:
                sqlStr = "select name, point from gift_v2 where uuid = '09875a92-8ab3-44bc-a83f-f9da6d5b6619'"
                result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
                lastmonthList.append({'name': result[0][0], 'point': result[0][1], 'create_at': int((datetime.strptime(sendDatetime, '%Y-%m-%d %H:%M:%S') + (timedelta(hours=8))).strftime('%s'))})
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title, current_count, total_users) values ('" 
        sqlStr += begDatetime + "', '" + endDatetime + "', '" + idlist[0] + "', '" + rtmp_url + "', 0, 350, 0, 0, 0)" 
        sqlList.append(sqlStr)
        if data1[i]['point'] > 0:    
            sqlStr = "insert into live_room_gift set consumption_point = " + str(data1[i]['point'])
            sqlStr += ", create_at = '" + sendDatetime + "', "
            sqlStr += "create_user_id = '" +  idlist[2]  + "', "
            sqlStr += "room_id = (select max(id) from live_room), status = 0, "
            if data1[i]['giftid'] != '':
                sqlStr += "gift_id = '" + data1[i]['giftid'] + "', "
            sqlStr += "target_user_id = '" +  idlist[0] + "', "
            sqlStr += "barrage_id = " + str(data1[i]['barrageid'])       
        else:
            sqlStr = "insert into liveshow(liveshow_id, title, start_time, end_time, liveshow_type, pool_id, gift_category, create_at, update_at) values ('" + str(int(time.time())) + "', " 
            sqlStr += "'report test', '" + begDatetime + "', '" + endDatetime + "', 'individual', '" +  idlist[0] + "', 74, '" + begDatetime + "', '" + begDatetime + "')"
            sqlList.append(sqlStr)
            sqlStr = "insert into liveshow_team set liveshow = (select max(id) from liveshow), team_id = 'test1', "
            sqlStr += "name = 'QA test', create_at = '" + begDatetime + "', update_at = '" + begDatetime + "'"
            sqlList.append(sqlStr)
            sqlStr = "insert into liveshow_gift_history set liveshow = (select max(id) from liveshow), team = (select max(id) from liveshow_team), "
            sqlStr += "giver_user_id = '" + idlist[2] + "', "
            sqlStr += "live_master_id = '" +idlist[0] + "', "
            sqlStr += "room_id = (select max(id) from live_room), gift_id = '09875a92-8ab3-44bc-a83f-f9da6d5b6619', "
            sqlStr += "points = 50, ratio = 2.00, "
            sqlStr += "create_at = '" + sendDatetime + "'"
        sqlList.append(sqlStr)             
    dbConnect.dbSetting(test_parameter['db'], sqlList)

class TestReceiveGiftTotal():
    def sendPostGift(self):
        sql = "select g.id, g.name, g.point from gift_v2 g join gift_category_v2 gc on category_id = gc.id where gc.type = 'post_gift' and g.point > 0"
        dbResult = dbConnect.dbQuery(test_parameter['db'], sql)
        giftId = dbResult[0][0]
        giftName = dbResult[0][1]
        giftPoint = dbResult[0][2]
        header['X-Auth-Token'] = test_parameter['broadcaster2_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster2_nonce']        
        apiName = '/api/v2/liveMaster/photoPost'
        body = {"photoPath": test_parameter['photo_url'], "content": "動態送禮。。測試中"}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/liveMaster/' + idlist[4] + '/photoPost?item=5&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        postId = restext['data'][0]['id']
        apiName = '/api/v2/identity/sendGift'
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']         
        body = {'giftId': giftId, 'postId': postId}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        today1List.append({'name': giftName, 'point': giftPoint, 'createAt': int(time.time())}) 


    def sendMessage(self):
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster2_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster2_nonce']             
        content = '哈囉，你好。歡迎來到Truelove😄😄😄 ' 
        body = { 
        "receiver": idlist[3],
        "msgType": "text",
        "textContent": content,
        "imageUrl": "",
        "previewUrl": "",
        "videoUrl": "",
        "origin": "giftGiversToSendIM"
        }
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']      
        content = '哈囉，你好。我是你的小粉絲😄😄😄 ' 
        body = { 
        "receiver": idlist[4],
        "msgType": "text",
        "textContent": content,
        "imageUrl": "",
        "previewUrl": "",
        "videoUrl": "",
        "origin": "giftGiversToSendIM"
        }
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)  
        today1List.append({'name': '20點聊天訊息', 'point': 20, 'createAt': int(time.time())}) 
     

    def createDictionary(self, sender, receiver, t1, y1, last1):
        #pprint(todayList)
        #pprint(yesterdayList)
        #pprint(lastmonthList)
        if len(t1) > 1:
            sorted(t1, key=attrgetter('create_at'), reverse=True)
        if len(y1) > 1:
            sorted(y1, key=attrgetter('create_at'), reverse=True)
        if len(last1) > 1:
            sorted(last1, key=attrgetter('create_at'), reverse=True)
        UserInfo[sender] = [{'liveMaster': receiver,
                            'today': t1,
                            'yesterday': y1,
                            'lastmonth': last1}]

    @pytest.fixture(scope='class')
    def addTestData(self):
        #print('add history data')
        dataDateIs = (datetime.today() - timedelta(days=datetime.today().day+2)).strftime('%Y-%m-%d')
        createHistoryData(dataDateIs, 'lastmonth')
        dataDateIs = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        createHistoryData(dataDateIs, 'yesterday') 
        self.createDictionary(idlist[2], idlist[0], todayList, yesterdayList, lastmonthList) 
        #pprint(UserInfo)
        self.sendMessage()
        self.sendPostGift()
        self.createDictionary(idlist[3], idlist[4], today1List, [], []) 
        #pprint(UserInfo)


    @pytest.mark.parametrize("auth, queryDate, isTimeCorrect, isBodyNull, liveaMaster, sender, expected", [
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], 'today', True, False, idlist[0], idlist[2], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], 'yesterday', True, False, idlist[0], idlist[2], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], 'lastmonth', True, False, idlist[0], idlist[2], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce']], 'lastmonth', True, True, idlist[0], idlist[2], 2),
        ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce']], 'today', True, False, idlist[1], idlist[0], 2),  
        ([test_parameter['broadcaster2_token'], test_parameter['broadcaster2_nonce']], 'today', True, False, idlist[4], idlist[3], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce']], 'today', True, False, idlist[0], idlist[2], 4),
        ([test_parameter['err_token'], test_parameter['err_nonce']], 'today', True, False, idlist[0], idlist[2], 4)
    ])
    def testGetTotalList(self, addTestData, auth, queryDate, isTimeCorrect, isBodyNull, liveaMaster, sender, expected):
        totalPoint = 0
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/total?item=1&page=1'
        header['X-Auth-Token'] = auth[0]
        header['X-Auth-Nonce'] = auth[1]        
        header['Content-Type'] = 'application/json'
        apiName1 = apiName.replace('{user id}', liveaMaster)
        if queryDate == 'today':
            start_at = int(datetime.strptime(((datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
            end_at = int((datetime.today() - timedelta(hours=8)).strftime('%s'))
        elif queryDate == 'yesterday':
            start_at = int(datetime.strptime(((datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
            end_at = int(datetime.strptime(((datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
        else:
            start_at = int(datetime.strptime(((datetime.today() - timedelta(days=datetime.today().day+15)).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
            end_at = int(datetime.strptime(((datetime.today() - timedelta(days=datetime.today().day+1)).strftime('%Y-%m-%d 15:59:59')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
        if isBodyNull:
            body = {}
        else:
            if isTimeCorrect:
                body = {'startTime': start_at, 'endTime': end_at}
            else: 
                body = {'startTime': start_at * 1000, 'endTime': end_at * 1000}
        pprint(body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            pprint(restext)
            pprint(UserInfo)
            if sender in UserInfo:
                if isBodyNull:
                    checklist = ['today', 'lastmonth', 'yesterday']
                    for j in checklist:
                        for i in UserInfo[sender][0][j]:
                            totalPoint += i['point']
                else:
                    for i in UserInfo[sender][0][queryDate]:
                        totalPoint += i['point']
                assert restext['data'][0]['points'] == totalPoint
            else:
                assert restext['totalCount'] == 0
            

 