#milestone18 加入動態贈禮
import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import sundry
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
create_At = int(time.time())
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
giftList = ['07a0592e-5024-4f9a-82ec-d209cea5b7f6', 120000,  #077
            '08303266-bade-4934-a223-800cbe0d94fa', 600000,  #177
            '253b4361-1b0d-499d-9943-4452ab81a88c', 100000,  #277
            '389715fd-88fd-43ae-938c-00c152c3c53b', 200000,  #077
            '3a99582d-349e-42ca-b8d8-258b7e204566', 50000,   #177
            '4db5bbaa-fd4d-4fcd-a84d-6d84d99dc58a', 10000,
            '57cfc4a6-92f3-4c9f-86e5-045e3a5ba2fa', 2000000, #077
            '82bf8567-82e3-4e3a-b214-f543db589ed1', 70000,   #177
            '93364e78-6e3b-442d-9eca-d37d491666ef', 1200, 
            'a0974c79-b468-47b5-a1a4-7e8e3c3592f7', 30000,  #077
            'e6e8aed2-7571-4516-8376-78d1dd4031a0', 3000,   #177
            'ebb24748-0ff3-42a1-8e26-e809e2f5fadf', 5000,
            'fd514de8-fdfb-4c56-9170-a9d92ffa125a', 600000] #077
BClist = []
URlist = []
category74 = {}
top5Master = {}
totalPoint = {}
category74Formaster = {}
newMaster = {}
totalMaster = {}
liveTimeSum = {}

def OneToOneMessage():
    sqlList = []
    sqlList.append("update remain_points set remain_points = 50 where identity_id = '" + URlist[2] + "'")
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    result = api.user_login(test_parameter['prefix'], 'broadcaster100', test_parameter['user_pass'])
    header['X-Auth-Token'] = result['token']
    header['X-Auth-Nonce'] = result['nonce']
    apiName = '/api/v2/liveMaster/instantMessage'
    content = '哈囉，你好。歡迎來到Truelove😄😄😄 ' 
    body = { 
    "receiver": URlist[2],
    "msgType": "text",
    "textContent": content,
    "imageUrl": "",
    "previewUrl": "",
    "videoUrl": "",
    "origin": "giftGiversToSendIM"
    }
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/identity/instantMessage'
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']      
    content = '哈囉，你好。我是你的小粉絲😄😄😄 ' 
    body = { 
    "receiver": BClist[15],
    "msgType": "text",
    "textContent": content,
    "imageUrl": "",
    "previewUrl": "",
    "videoUrl": "",
    "origin": "giftGiversToSendIM"
    }
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)  
    totalPoint[URlist[2]] += 20
    

def sendGiftToPost(masterid, userid):
    sql = "select g.id, g.point from gift g join gift_category gc on category_id = gc.id where gc.type = 'post_gif'"
    dbResult = dbConnect.dbQuery(test_parameter, sql)
    giftId = dbResult[0][0]
    giftPoint = dbResult[0][1]
    result = api.user_login(test_parameter['prefix'], 'broadcaster100', test_parameter['user_pass'])
    header['X-Auth-Token'] = result['token']
    header['X-Auth-Nonce'] = result['nonce']      
    apiName = '/api/v2/liveMaster/photoPost'
    body = {"photoPath": test_parameter['photo_url'], "content": "動態送禮。。測試中"}
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/liveMaster/' + masterid + '/photoPost?item=5&page=1'
    res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
    restext = json.loads(res.text)
    postId = restext['data'][0]['id']
    result = api.user_login(test_parameter['prefix'], 'track0077', test_parameter['user_pass'])
    header['X-Auth-Token'] = result['token']
    header['X-Auth-Nonce'] = result['nonce']      
    apiName = '/api/v2/identity/sendGift'
    body = {'giftId': giftId, 'postId': postId}
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    totalPoint[userid] += giftPoint
    totalMaster[masterid] += giftPoint
    newMaster[masterid] += giftPoint


def setup_module():
    sqlList = []
    initdata.set_test_data(env, test_parameter)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
    for i in range(85, 101):
        if i // 10 < 10:
            account = 'broadcaster0' + str(i)
        else:
            account = 'broadcaster' + str(i)
        BClist.append(api.search_user(test_parameter['prefix'], account, header))
    for i in range(3):
        if i > 0:
            account = 'track0' + str(i * 100 + 77)
        else:
            account = 'track0077'
        URlist.append(api.search_user(test_parameter['prefix'], account, header))
    initdata.resetData(test_parameter['db'], BClist[0])
    tableList = ['liveshow_gift_history', 'live_room_gift', 'live_room']   
    for i in tableList:
        if i == 'live_room':
            sqlStr = "delete from " + i + " where chat_server_id = 350"
            sqlList.append(sqlStr)
        elif i == 'live_room_gift':
            for k in URlist:
                sqlStr = "delete from " + i + " where create_user_id = '" +  k + "'"
                sqlList.append(sqlStr)
        else:
            for k in URlist:
                sqlStr = "delete from " + i + " where giver_user_id = '" +  k + "'"
                sqlList.append(sqlStr)
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    sqlList.clear()
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
    for i in range(85, 101):
        if i // 10 < 10:
            account = 'broadcaster0' + str(i)
        else:
            account = 'broadcaster' + str(i)
        BClist.append(api.search_user(test_parameter['prefix'], account, header))
    for i in range(3):
        if i > 0:
            account = 'track0' + str(i * 100 + 77)
        else:
            account = 'track0077'
        URlist.append(api.search_user(test_parameter['prefix'], account, header))
    for i in range(13):    
        k = i % 3    
        if giftList[i * 2] in ('253b4361-1b0d-499d-9943-4452ab81a88c', '57cfc4a6-92f3-4c9f-86e5-045e3a5ba2fa', 'fd514de8-fdfb-4c56-9170-a9d92ffa125a'):
            if URlist[k] in category74:
                category74[URlist[k]] += giftList[i * 2 + 1]
            else:
                category74[URlist[k]] = giftList[i * 2 + 1]
        if i < 5:
            if URlist[k] in top5Master:
                top5Master[URlist[k]] += giftList[i * 2 + 1]
            else:
                top5Master[URlist[k]] = giftList[i * 2 + 1]
        if URlist[k] in totalPoint:
            totalPoint[URlist[k]] += giftList[i * 2 + 1]
        else:
            totalPoint[URlist[k]] = giftList[i * 2 + 1]
        sqlStr = "insert into live_room_gift(consumption_point, create_at, create_user_id, room_id, status, gift_id, target_user_id) value`s (" + str(giftList[i * 2 + 1])
        sqlStr += ", FROM_UNIXTIME(" + str(create_At + i * 120) + ", '%Y-%m-%d %H:%i:%s'), '" + URlist[k] + "', 5487, 0, '" + giftList[i * 2] + "', '" + BClist[i] + "')"        
        sqlList.append(sqlStr)    
        begDatetime = datetime.fromtimestamp(create_At - 2) + timedelta(hours=-8)
        endDatetime = datetime.fromtimestamp(create_At + (600 + i * 120)) + timedelta(hours=-8)
        liveTimeSum[BClist[i]] = endDatetime - begDatetime        
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime.strftime('%Y-%m-%d %H:%M:%S') + "', '"
        sqlStr += endDatetime.strftime('%Y-%m-%d %H:%M:%S') + "', '" + BClist[i] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"   
        sqlList.append(sqlStr)
    Barrage = [35, 350]
    for i in range(13, 15):
        k = i % 3    
        totalPoint[URlist[k]] += Barrage[i % 13]
        sqlStr = "insert into live_room_gift(consumption_point, create_at, create_user_id, room_id, status, barrage_id, target_user_id) values (" + str(Barrage[i % 13])
        sqlStr += ", FROM_UNIXTIME(" + str(create_At + i * 120) + ", '%Y-%m-%d %H:%i:%s'), '" + URlist[k] + "', 5487, 0, '" + str(i % 13 + 1) + "', '" + BClist[i] + "')"        
        sqlList.append(sqlStr)        
        begDatetime = datetime.fromtimestamp(create_At - 2) + timedelta(hours=-8)
        endDatetime = datetime.fromtimestamp(create_At + (600 + i * 120)) + timedelta(hours=-8)
        liveTimeSum[BClist[i]] = endDatetime - begDatetime 
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime.strftime('%Y-%m-%d %H:%M:%S') + "', '"
        sqlStr += endDatetime.strftime('%Y-%m-%d %H:%M:%S') + "', '" + BClist[i] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"   
        sqlList.append(sqlStr)
    for i in range(10, 12):
        totalPoint[URlist[2]] += giftList[i * 2 + 1]
        sqlStr = "insert into liveshow_gift_history(liveshow, team, giver_user_id, live_master_id, room_id, gift_id, points, ratio, create_at) values (1, 148, '"
        sqlStr += URlist[2] + "', '" + BClist[15] + "', 4567, '" + giftList[i * 2] + "'," + str(giftList[i * 2 + 1]) + ", 2.00, FROM_UNIXTIME(" + str(create_At + i * 150) + ", '%Y-%m-%d %H:%i:%s'))"
        sqlList.append(sqlStr)   
    OneToOneMessage  # 加入1對1私訊資料
    sendGiftToPost(BClist[15], URlist[0]) #加入動態送禮
    for i in range(3):
        sqlStr = "update user_experience set experience = " + str(48000000 + i * 10000) + " where identity_id = '" + BClist[i] + "'"
        if i > 0:
            sqlStr2 = "delete from new_live_master where live_master_id = '" + BClist[i] + "'"
            sqlList.extend([sqlStr, sqlStr2])        
        else:
            sqlList.append(sqlStr)
    dbConnect.dbSetting(test_parameter['db'], sqlList)

    
def teardown_module():
    pass

class TestgiftGiver():
    def testGiver_case1(self):
        #以送禮類別做查詢條件
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
        apiName = '/api/v2/ranking/giftGiver'
        sTime = datetime.fromtimestamp(create_At).strftime('%Y-%m-%d %H:%M:%S')
        eTime = datetime.fromtimestamp(create_At + 16 * 120).strftime('%Y-%m-%d %H:%M:%S')
        body = {'giftCategory': 74,
                'startTime': sTime,
                'endTime': eTime}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == len(category74)
        for i in range(len(restext['data'])):
            assert restext['data'][i]['userId'] in category74
            assert restext['data'][i]['points'] == category74[restext['data'][i]['userId']]
            assert restext['data'][i]['ranking'] == i + 1

    def testGiver_case2(self):
        #以直播主ID做查詢條件
        masterList = []
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        apiName = '/api/v2/ranking/giftGiver'
        sTime = datetime.fromtimestamp(create_At).strftime('%Y-%m-%d %H:%M:%S')
        eTime = datetime.fromtimestamp(create_At + 16 * 120).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(5):
            masterList.append(BClist[i])
        body = {'liveMasterId': masterList,
                'startTime': sTime,
                'endTime':eTime}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        #pprint(restext)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == len(top5Master)
        for i in range(len(restext['data'])):
            assert restext['data'][i]['userId'] in top5Master
            assert restext['data'][i]['points'] == top5Master[restext['data'][i]['userId']]
            assert restext['data'][i]['ranking'] == i + 1

    def testGiver_case3(self):
        #以送禮時間為查詢條件
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        apiName = '/api/v2/ranking/giftGiver'
        sTime = datetime.fromtimestamp(create_At).strftime('%Y-%m-%d %H:%M:%S')
        eTime = datetime.fromtimestamp(create_At + 16 * 120).strftime('%Y-%m-%d %H:%M:%S')
        body = {'startTime': sTime,
                'endTime':eTime}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        print(body)
        pprint(restext)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == len(totalPoint)
        for i in range(len(restext['data'])):
            assert restext['data'][i]['userId'] in totalPoint
            assert restext['data'][i]['points'] == totalPoint[restext['data'][i]['userId']]
            assert restext['data'][i]['ranking'] == i + 1

    def testGiver_case4(self):
        #查無資料
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        apiName = '/api/v2/ranking/giftGiver'
        sTime = datetime.fromtimestamp(create_At + 20 * 120).strftime('%Y-%m-%d %H:%M:%S')
        eTime = datetime.fromtimestamp(create_At + 22 * 120).strftime('%Y-%m-%d %H:%M:%S')
        body = {'startTime': sTime,
                'endTime':eTime}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2
