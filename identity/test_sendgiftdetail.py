#milestone18 加入動態贈禮
import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)


def teardown_module():
    pass   


class TestSendGiftDetail():
    idlist = []
    create_At = int(time.time()) - 28800
    postId =  ''
    giftId = ''
    giftName = ''
    giftPoint = ''

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
        sqlStr += str(self.create_At) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[2] + "', 127272.72726, 5487, 54545.45454, 0, 'fd514de8-fdfb-4c56-9170-a9d92ffa125a', '" + self.idlist[0] + "')"
        sqlStr1 = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, target_user_id, barrage_id) values (0, 35,  FROM_UNIXTIME("
        sqlStr1 += str(self.create_At + 5) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[2] + "', 7.4242, 5487, 3.1818, 0, '" + self.idlist[0] + "', 1)"
        sqlStr2 = "insert into live_room_gift(agency_amount, consumption_point, create_at, create_user_id, master_amount, room_id, service_amount, status, target_user_id, barrage_id) values (0, 350,  FROM_UNIXTIME("
        sqlStr2 += str(self.create_At + 10) + ", '%Y-%m-%d %H:%i:%s'), '" + self.idlist[2] + "', 74.24242, 5487, 31.81818, 0, '" + self.idlist[0] + "', 2)"
        sqlStr3 = "insert into liveshow_gift_history(liveshow, team, giver_user_id, live_master_id, room_id, gift_id, points, ratio, create_at) values (1, 148, '"
        sqlStr3 += self.idlist[2] + "', '" + self.idlist[0] + "', 4567, '09875a92-8ab3-44bc-a83f-f9da6d5b6619', 56, 2.00, FROM_UNIXTIME(" + str(self.create_At + 120) + ", '%Y-%m-%d  %H:%i:%s'))"
        sqlList.extend([sqlStr, sqlStr1, sqlStr2, sqlStr3])
        sqlList.append("update remain_points set remain_points = 100 where identity_id = '" + self.idlist[2] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def teardown_class(self):
        pass

    def preparePostGift(self):
        sql = "select g.id, g.name, g.point from gift g  join gift_category gc on category_id = gc.id where gc.type = 'post_gif'"
        dbResult = dbConnect.dbQuery(test_parameter, sql)
        self.giftId = dbResult[0][0]
        self.giftName = dbResult[0][1]
        self.giftPoint = dbResult[0][2]
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']        
        apiName = '/api/v2/liveMaster/photoPost'
        body = {"photoPath": test_parameter['photo_url'], "content": "動態送禮。。測試中"}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/liveMaster/' + self.idlist[0] + '/photoPost?item=5&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        self.postId = restext['data'][0]['id']

    def testConditionIsMinisec(self):
        #時間為毫秒
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': self.create_At * 1000, 'endTime': (self.create_At + 5) * 1000}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert res.status_code // 100 != 5

    def testBodyIsEmpty(self):
        #時間條件空值
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=1&page=1'    
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert res.status_code // 100 == 2        

    def testWrongAuth(self):
        #token/noce錯誤
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=1&page=1'    
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': self.create_At , 'endTime': (self.create_At + 5)}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        assert int(res.status_code / 100) == 4

    def testGiftListIsEmpty(self):
        #未送出任何禮物
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=1&page=1'    
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[3])
        body = {'startTime': self.create_At, 'endTime': (self.create_At + 5)}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 0

    def testConditionOfTime(self):
        #時間區間測試
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=1&page=1'    
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': self.create_At , 'endTime': self.create_At + 130}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 4

    def testVerifyResult(self):
        #資料確認
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=10&page=1'    
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': self.create_At + 5, 'endTime': self.create_At + 5}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['giftPoint'] == 35
        assert restext['data'][0]['user']['id'] == self.idlist[0]
        assert restext['data'][0]['createAt'] == self.create_At + 5
        assert restext['data'][0]['giftName'] == '35點彈幕訊息'

    def testSendMessage(self):
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
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=10&page=1'    
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        apiName1 = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': send_at - 1, 'endTime': send_at + 2}
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['giftPoint'] == 20
        assert restext['data'][0]['user']['id'] == self.idlist[0]
        assert restext['data'][0]['giftName'] == '20點傳送訊息'

    def testSendGiftToPhoto(self):
        #動態贈禮
        self.preparePostGift
        send_at = int(time.time())
        apiName = '/api/v2/identity/sendGift'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']         
        body = {'giftId': self.giftId, 'postId': self.postId}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        apiName = '/api/v2/identity/{user id}/sendGift/detail?item=10&page=1'       
        apiName = apiName.replace('{user id}', self.idlist[2])
        body = {'startTime': send_at - 1, 'endTime': send_at + 2}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 1
        assert restext['data'][0]['giftPoint'] == self.giftPoint
        assert restext['data'][0]['user']['id'] == self.idlist[0]
        assert restext['data'][0]['giftName'] == self.giftName
