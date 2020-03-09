import time
import json
import datetime
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import sundry
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
cards = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
liverRevenu
yesterday = {'playTime': 0, 'points': 0}
today = {'playTime': 0, 'points': 0}


def liveRoomGift(startDate, masterId):
    rtmp_url = 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605'
    sqlList = []
    data1 = [{'start_at': ' 01:30:00',
    'end_at': ' 01:40:00',
    'send_at': ' 01:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 03:30:00',
    'end_at': ' 03:40:00',
    'send_at': ' 03:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 05:30:00',
    'end_at': ' 05:40:00',
    'send_at': ' 05:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 07:30:00',
    'end_at': ' 08:00:00',
    'send_at': ' 07:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 08:05:00',
    'end_at': ' 09:40:00',
    'send_at': ' 09:31:00',
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
    {'start_at': ' 15:05:00',
    'end_at': ' 15:40:00',
    'send_at': ' 15:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 15:50:00',
    'end_at': ' 16:31:00',
    'send_at': ' 15:51:00',
    'point': 3000,
    'giftid': 'e6e8aed2-7571-4516-8376-78d1dd4031a0',
    'barrageid': 'NULL'}]
    continueRecord = -1
    for i in range(len(data1)):
        begDatetime = startDate + data1[i]['start_at']
        endDatetime = startDate + data1[i]['end_at']
        if dictype['playTime'] == 0:
            if int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) >= 3600:
                dictype['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
            elif (len(data1) - i > 1):
                begDatetime1 = startDate + data1[i + 1]['start_at']
                endDatetime1 = startDate + data1[i + 1]['end_at']
                if int((datetime.strptime(begDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) <= 300:
                    if int((datetime.strptime(endDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) >= 3600:
                        continueRecord = i + 1                
                        dictype['playTime'] += int((datetime.strptime(endDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        else:
            if i != continueRecord:
                dictype['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        if isYesterdate and (data1[i]['send_at'] >= ' 16:00:00'):
            today['points'] += data1[i]['point']  
            print('add today point')              
        else:
            dictype['points'] += data1[i]['point']            
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', '" + rtmp_url + "', 0, 350, 0)" 
        sqlList.append(sqlStr)
        if data1[i]['point'] > 0:    
            sendDatetime = startDate + data1[i]['send_at']
            sqlStr = "insert into live_room_gift set consumption_point = " + str(data1[i]['point'])
            sqlStr += ", create_at = '" + sendDatetime + "', "
            sqlStr += "create_user_id = '" +  idlist[2]  + "', "
            sqlStr += "room_id = (select max(id) from live_room), status = 0, "
            if data1[i]['giftid'] != '':
                sqlStr += "gift_id = '" + data1[i]['giftid'] + "', "
            sqlStr += "target_user_id = '" +  idlist[0] + "', "
            sqlStr += "barrage_id = " + str(data1[i]['barrageid'])       
        else:
            sqlStr = "insert into liveshow_gift_history set liveshow = 1, team = 148, "
            sqlStr += "giver_user_id = '" + idlist[2] + "', "
            sqlStr += "live_master_id = '" +idlist[0] + "', "
            sqlStr += "room_id = (select max(id) from live_room), gift_id = '09875a92-8ab3-44bc-a83f-f9da6d5b6619', "
            sqlStr += "points = 56, ratio = 2.00, "
            sqlStr += "create_at = '" + sendDatetime + "'"
            dictype['points'] += 56
        sqlList.append(sqlStr)          
    dictype['playTime'] = 10800 if dictype['playTime'] > 10800 else None       
    dbConnect.dbSetting(test_parameter['db'], sqlList)

def liveShowHGift(startDate, masterId):
        rtmp_url = 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605'
    sqlList = []
    data1 = [{'start_at': ' 01:30:00',
    'end_at': ' 01:40:00',
    'send_at': ' 01:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 03:30:00',
    'end_at': ' 03:40:00',
    'send_at': ' 03:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 05:30:00',
    'end_at': ' 05:40:00',
    'send_at': ' 05:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 07:30:00',
    'end_at': ' 08:00:00',
    'send_at': ' 07:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 08:05:00',
    'end_at': ' 09:40:00',
    'send_at': ' 09:31:00',
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
    {'start_at': ' 15:05:00',
    'end_at': ' 15:40:00',
    'send_at': ' 15:31:00',
    'point': 1200,
    'giftid': '93364e78-6e3b-442d-9eca-d37d491666ef',
    'barrageid': 'NULL'},
    {'start_at': ' 15:50:00',
    'end_at': ' 16:31:00',
    'send_at': ' 15:51:00',
    'point': 3000,
    'giftid': 'e6e8aed2-7571-4516-8376-78d1dd4031a0',
    'barrageid': 'NULL'}]
    continueRecord = -1
    for i in range(len(data1)):
        begDatetime = startDate + data1[i]['start_at']
        endDatetime = startDate + data1[i]['end_at']
        if dictype['playTime'] == 0:
            if int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) >= 3600:
                dictype['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
            elif (len(data1) - i > 1):
                begDatetime1 = startDate + data1[i + 1]['start_at']
                endDatetime1 = startDate + data1[i + 1]['end_at']
                if int((datetime.strptime(begDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) <= 300:
                    if int((datetime.strptime(endDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) >= 3600:
                        continueRecord = i + 1                
                        dictype['playTime'] += int((datetime.strptime(endDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        else:
            if i != continueRecord:
                dictype['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        if isYesterdate and (data1[i]['send_at'] >= ' 16:00:00'):
            today['points'] += data1[i]['point']  
            print('add today point')              
        else:
            dictype['points'] += data1[i]['point']            
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', '" + rtmp_url + "', 0, 350, 0)" 
        sqlList.append(sqlStr)
        if data1[i]['point'] > 0:    
            sendDatetime = startDate + data1[i]['send_at']
            sqlStr = "insert into live_room_gift set consumption_point = " + str(data1[i]['point'])
            sqlStr += ", create_at = '" + sendDatetime + "', "
            sqlStr += "create_user_id = '" +  idlist[2]  + "', "
            sqlStr += "room_id = (select max(id) from live_room), status = 0, "
            if data1[i]['giftid'] != '':
                sqlStr += "gift_id = '" + data1[i]['giftid'] + "', "
            sqlStr += "target_user_id = '" +  idlist[0] + "', "
            sqlStr += "barrage_id = " + str(data1[i]['barrageid'])       
        else:
            sqlStr = "insert into liveshow_gift_history set liveshow = 1, team = 148, "
            sqlStr += "giver_user_id = '" + idlist[2] + "', "
            sqlStr += "live_master_id = '" +idlist[0] + "', "
            sqlStr += "room_id = (select max(id) from live_room), gift_id = '09875a92-8ab3-44bc-a83f-f9da6d5b6619', "
            sqlStr += "points = 56, ratio = 2.00, "
            sqlStr += "create_at = '" + sendDatetime + "'"
            dictype['points'] += 56
        sqlList.append(sqlStr)          
    dictype['playTime'] = 10800 if dictype['playTime'] > 10800 else None       
    dbConnect.dbSetting(test_parameter['db'], sqlList)


def photoGift(masterId):
    #動態贈禮
    sqlStr = "select g.id, g.name, g.point from gift g  join gift_category gc on category_id = gc.id where where gc.type = 'post_gif'"
    dbResult = dbConnect.dbQuery(test_parameter, sqlStr)
    self.giftId = dbResult[0][0]
    self.giftName = dbResult[0][1]
    self.giftPoint = dbResult[0][2]
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']        
    apiName = '/api/v2/liveMaster/photoPost'
    body = {"photoPath": test_parameter['photo_url'], "content": "動態送禮。。測試中"}
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/liveMaster/' + idlist[0] + '/photoPost?item=5&page=1'
    res = api.apiFunctio(test_parameter['prefix'], header, apiName, 'get', None)
    restext = json.loads(res.text)
    self.postId = restext['data'][0]['id']
    send_at = int(time.time())
    apiName = '/api/v2/identity/sendGift'
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']         
    body = {'giftId': self.giftId, 'postId': self.postId}
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
    apiName1 = apiName.replace('{user id}', idlist[0])
    res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
    restext = json.loads(res.text)
    today['points'] += self.giftPoint


def imPoint(master, user):
    # 私訊收益
    sqlList = []
    sqlList.append("update remain_points set remain_points = 50 where identity_id = '" + idlist[2] + "'")
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    apiName = '/api/v2/liveMaster/instantMessage'
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
    content = '哈囉，你好。歡迎來到Truelove😄😄😄 ' 
    body = { 
    "receiver": idlist[2],
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
    "receiver": idlist[0],
    "msgType": "text",
    "textContent": content,
    "imageUrl": "",
    "previewUrl": "",
    "videoUrl": "",
    "origin": "giftGiversToSendIM"
    }
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)  
    apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
    apiName1 = apiName.replace('{user id}', idlist[0])
    res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
    restext = json.loads(res.text)
    today['points'] += 20
