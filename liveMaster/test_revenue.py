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
idlist = []   
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
yesterday = {'playTime': 0, 'points': 0}
lastmonth = {'playTime': 0, 'points': 0}
today = {'playTime': 0, 'points': 0}

def setup_module():
    initdata.set_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])


def teardown_module():
    pass


def createHistoryData(startDate, dictype, isYesterdate):
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


class TestRevenue():
    timeList = []
    checkList = []     
    postId =  ''
    giftId = ''
    giftName = ''
    giftPoint = ''
    rtmp_url = 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605'
    def setup_class(self):
        dataDateIs = (datetime.today() - timedelta(days=datetime.today().day+2)).strftime('%Y-%m-%d')
        createHistoryData(dataDateIs, lastmonth, False)
        dataDateIs = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        createHistoryData(dataDateIs, yesterday, True)    
        sundry.execut_calculate_statistics(test_parameter['db'])
        time.sleep(10)

    def teardown_class(self):
        pass
    
    def preparePostGift(self):
        sql = "select g.id, g.name, g.point from gift g  join gift_category gc on category_id = gc.id where where gc.type = 'post_gif'"
        dbResult = dbConnect.dbQuery(test_parameter, sql)
        self.giftId = dbResult[0][0]
        self.giftName = dbResult[0][1]
        self.giftPoint = dbResult[0][2]
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']        
        apiName = '/api/v2/liveMaster/photoPost'
        body = {"photoPath": test_parameter['photo_url'], "content": "動態送禮。。測試中"}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/liveMaster/' + idlist[0] + '/photoPost?item=5&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        self.postId = restext['data'][0]['id']

    def insertData(self, sqlList):
        #pprint(sqlList)
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        #pass

    def testVerifyHistoryData(self):
        # 比對歷史資料
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + lastmonth['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + lastmonth['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']
    
    def testRevene_firstLiveWithout1hour(self):
        #當日首次開播未滿1時不計
        sqlList = []
        dateInfo = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d')
        begDatetime = dateInfo + ' 07:00:00'
        endDatetime = dateInfo + ' 07:29:58'
        sendDatetime = dateInfo + ' 07:00:51'
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"        
        sqlList.append(sqlStr) 
        sqlStr = "insert into live_room_gift set consumption_point = 600000, "
        sqlStr += "create_at = '" + sendDatetime + "', "
        sqlStr += "create_user_id = '" +  idlist[2]  + "', "
        sqlStr += "room_id = (select max(id) from live_room), status = 0, "
        sqlStr += "gift_id = 'fd514de8-fdfb-4c56-9170-a9d92ffa125a', " 
        sqlStr += "target_user_id = '" +  idlist[0] + "'"
        sqlList.append(sqlStr)
        self.insertData(sqlList)
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        restext = json.loads(res.text)
        today['points'] += 600000
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + lastmonth['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + lastmonth['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']

    def testRevene_liveTwiceIn5min(self):
        #開播斷訊，5分鐘內再開播皆會接著算
        #禮物
        sqlList = []
        dateInfo = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d')
        begDatetime = dateInfo + ' 08:30:00'
        endDatetime = dateInfo + ' 08:55:00'
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"        
        sqlList.append(sqlStr) 
        begDatetime1 = dateInfo + ' 09:00:00'
        endDatetime1 = dateInfo + ' 09:35:00'    
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime1 + "', '" + endDatetime1 + "', '"
        sqlStr += idlist[0] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"        
        sqlList.append(sqlStr)
        self.insertData(sqlList)
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        restext = json.loads(res.text)
        today['playTime'] += int((datetime.strptime(endDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + lastmonth['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + lastmonth['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']

    def testRevene_firstLiveWith1hour(self):
        #首次開播滿1小時後，之後無論時間長短月報表皆計入
        #彈幕
        sqlList = []
        dateInfo = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d')
        begDatetime = dateInfo + ' 11:30:00'
        endDatetime = dateInfo + ' 11:40:00'
        sendDatetime = dateInfo + ' 11:32:00'
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"        
        sqlList.append(sqlStr) 
        sqlStr = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, target_user_id, barrage_id) values (0, 350, '"
        sqlStr += sendDatetime + "', '" + idlist[2] + "', 74.24242, 5487, 31.81818, 0, '" + idlist[0] + "', 2)"
        sqlList.append(sqlStr) 
        self.insertData(sqlList)
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        restext = json.loads(res.text)
        today['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        today['points'] += 350
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + lastmonth['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + lastmonth['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']

    def testRevene_liveTimeOver3hours(self):
        #每日最多以3小時
        #liveshow送禮
        sqlList = []
        dateInfo = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d')
        begDatetime = dateInfo + ' 14:30:00'
        endDatetime = dateInfo + ' 16:50:00'
        sendDatetime = dateInfo + ' 16:32:00'
        sqlStr = "insert into live_room(create_at, end_at, live_master_id, rtmp_url, status, chat_server_id, title) values ('" + begDatetime + "', '" + endDatetime + "', '"
        sqlStr += idlist[0] + "', 'rtmp://ottworigin2.media.hinet.net/live_angel06/3955fd05-309f-4a07-a8a2-a2bb6146e605', 0, 350, 0)"        
        sqlList.append(sqlStr) 
        sqlStr = "insert into liveshow_gift_history set liveshow = 1, team = 148, "
        sqlStr += "giver_user_id = '" + idlist[2] + "', "
        sqlStr += "live_master_id = '" +idlist[0] + "', "
        sqlStr += "room_id = (select max(id) from live_room), gift_id = '09875a92-8ab3-44bc-a83f-f9da6d5b6619', "
        sqlStr += "points = 56, ratio = 2.00, "
        sqlStr += "create_at = '" + sendDatetime + "'"
        sqlList.append(sqlStr) 
        self.insertData(sqlList)
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        restext = json.loads(res.text)
        today['playTime'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        today['playTime'] = 10800 if today['playTime'] > 10800 else None            
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points'] 
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points'] 
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + lastmonth['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + lastmonth['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']

    def testWithoutAth(self):
        # token/nonce 不存在
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        assert res.status_code // 100 in (4, 5)

    def testUidNotExist(self):
        #user id不存在
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', 'a12303495-1024kd-92e4js-1938f')
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        assert res.status_code // 100 == 4

    def testUidNotMatchAuth(self):
        apiName = '/api/v2/liveMaster/{user id}/revenue/summary'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', idlist[2])
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', {})
        assert res.status_code // 100 == 4

    def testReveneFromIM(self):
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
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + today['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']

    def testSendGiftToPhoto(self):
        #動態贈禮
        self.preparePostGift
        #send_at = int(time.time())
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
        assert res.status_code // 100 == 2
        assert restext['today']['points'] == today['points']
        assert restext['today']['liveTimeSec'] == today['playTime']
        assert restext['yesterday']['points'] == yesterday['points']
        assert restext['yesterday']['liveTimeSec'] == yesterday['playTime']
        if datetime.today().day == 1:
            assert restext['thisMonth']['liveTimeSec'] == today['playTime']      
            assert restext['thisMonth']['points'] == today['points']
        else:
            assert restext['thisMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['thisMonth']['points'] == yesterday['points'] + today['points']
        if datetime.today().day == 1:
            assert restext['lastMonth']['liveTimeSec'] == yesterday['playTime'] + today['playTime']      
            assert restext['lastMonth']['points'] == yesterday['points'] + today['points']
        else:
            assert restext['lastMonth']['points'] == lastmonth['points']
            assert restext['lastMonth']['liveTimeSec'] == lastmonth['playTime']