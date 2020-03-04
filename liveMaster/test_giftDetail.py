#milestone18 加入動態贈禮
import time
import json
import datetime
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import photo
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
cards = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    

def teardown_module():
    pass

class TestReceiveGiftDetail():
    idlist = []
    postId =  ''
    giftId = ''
    giftName = ''
    giftPoint = ''
    create_At = int((datetime.today() - timedelta(hours=8)).strftime('%s'))
    def setup_class(self):
        sqlList = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
        initdata.resetData(test_parameter['db'], self.idlist[0])
        sqlStr = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, gift_id, target_user_id) values (0, 600000, FROM_UNIXTIME("
        sqlStr += str(self.create_At) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[1] + "', 127272.72726, 5487, 54545.45454, 0, 'fd514de8-fdfb-4c56-9170-a9d92ffa125a', '" + self.idlist[0] + "')"
        sqlStr1 = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, target_user_id, barrage_id) values (0, 35,  FROM_UNIXTIME("
        sqlStr1 += str(self.create_At + 5) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[2] + "', 7.4242, 5487, 3.1818, 0, '" + self.idlist[0] + "', 1)"
        sqlStr2 = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, target_user_id, barrage_id) values (0, 350,  FROM_UNIXTIME("
        sqlStr2 += str(self.create_At + 10) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[3] + "', 74.24242, 5487, 31.81818, 0, '" + self.idlist[0] + "', 2)"
        sqlStr3 = "insert into liveshow_gift_history(liveshow, team, giver_user_id, live_master_id, room_id, gift_id, points, ratio, create_at) values (1, 148, '"
        sqlStr3 += self.idlist[2] + "', '" + self.idlist[0] + "', 4567, '09875a92-8ab3-44bc-a83f-f9da6d5b6619', 56, 2.00, FROM_UNIXTIME(" + str(self.create_At + 120) + ", '%Y-%m-%d  %H:%i:%s'))"
        sqlList.extend([sqlStr, sqlStr1, sqlStr2, sqlStr3])
        sqlList.append("update remain_points set remain_points = 100 where identity_id = '" + self.idlist[2] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)


    def sendPostGift(self):
        sqlStr = "select id, point from gift where category_id = 108 and status = 1"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        giftId = result[0][0]
        point = result[0][1]
        photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], test_parameter['photo_url'], 3)
        photoId = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], self.idlist[0])
        photo.sendPhotoGift(test_parameter['user1_token'], test_parameter['user1_nonce'], test_parameter['prefix'], photoId[0], giftId)
        return(point, giftId)

    def test_timeFormateIsMS(self):
        #資料格式不正確
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': self.create_At * 1000, 'endTime': (self.create_At + 5) * 1000}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert int(res.status_code / 100) == 4

    def test_bodyIsNull(self):
        #時間條件空值會全撈
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=20&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert restext['totalCount'] == 4
        assert restext['data'][0]['createAt'] >= restext['data'][1]['createAt']

    def test_case3(self):
        #一般使用者
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': self.create_At , 'endTime': (self.create_At + 5)}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert int(res.status_code / 100) == 4

    def test_case4(self):
        #token/noce錯誤
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': self.create_At , 'endTime': (self.create_At + 5)}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert int(res.status_code / 100) == 4

    def test_case5(self):
        #直播主從未收到禮物
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[1])
        body = {'startTime': self.create_At, 'endTime': (self.create_At + 5)}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 0

    def test_case6(self):
        #時間區間測試
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': self.create_At, 'endTime': (self.create_At + 130)}
        pprint(body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 4

    def test_case7(self):
        #資料確認
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': self.create_At + 4, 'endTime': self.create_At + 6}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['points'] == 35
        assert restext['data'][0]['user']['id'] == self.idlist[2]
        assert restext['data'][0]['createAt'] == self.create_At + 5
        assert restext['data'][0]['giftName'] == '35點彈幕訊息'

    def test_case8(self):
        #時間區間用毫秒會回錯誤而非internal error 
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': (self.create_At - 4) * 100, 'endTime': (self.create_At + 6) * 100}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert res.status_code // 100 != 5

    def test_case9(self):
        #不給時間區間會回錯誤而非internal error 
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert res.status_code // 100 != 5

    def testReceiveMessage(self):
        # 1對1私訊點數
        send_at = int(time.time())
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。歡迎來到Truelove😄😄😄 ' 
        body = { 
        "receiver": self.idlist[2],
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
        "receiver": self.idlist[0],
        "msgType": "text",
        "textContent": content,
        "imageUrl": "",
        "previewUrl": "",
        "videoUrl": "",
        "origin": "giftGiversToSendIM"
        }
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)  
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': send_at - 1, 'endTime': send_at + 3}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['points'] == 20
        assert restext['data'][0]['user']['id'] == self.idlist[2]
        assert restext['data'][0]['createAt'] >= send_at
        assert restext['data'][0]['giftName'] == '20點傳送訊息'

    def testSendGiftToPhoto(self):
        #動態贈禮
        send_at = int(time.time())
        result = self.sendPostGift()
        apiName = '/api/v2/liveMaster/{user id}/receiveGift/detail?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[0])
        body = {'startTime': send_at - 1, 'endTime': send_at + 3}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['points'] == result[0]
        assert restext['data'][0]['user']['id'] == self.idlist[3]
        assert restext['data'][0]['createAt'] == send_at
        assert restext['data'][0]['giftName'] == result[1]
