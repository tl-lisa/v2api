import json
import requests
import pymysql
import time
import string
import threading
import socket
from ..assistence import chatlib
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import sundry
from ..assistence import photo
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass   


class T():
    @staticmethod
    def SetTracking(header, way, mid):
        if way == 'post':
            apilink = '/api/v2/identity/track'
            body = {'liveMasterId': mid}        
        else:
            apilink = '/api/v2/identity/track/' + mid
            body = None            
        res = api.apiFunction(test_parameter['prefix'], header, apilink, way, body)            
        return res

    @staticmethod
    def GetMessage(uid, header, items):
        apilink = '/api/v2/identity/{user id}/notification/list?item=' + str(items) + '&page=1' 
        link = apilink.replace('{user id}', uid)       
        res = api.apiFunction(test_parameter['prefix'], header, link, 'get', None)
        return res 


class TestNotification():  
    idlist = [] 
    def setup_class(self):
        sqlList = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))        
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))        
        #update token； 清除DB data
        p_token = 'eUOePK4v6Xg:APA91bHqcnv2C7MSD9GMMTG2rs34cy4sVabpnNJ-hKqzjBzUHtWKHa84SRpZTQWDL7vX4b2tppZvFT25eXJerOVpBy_3xFWagcc6Z307JbJq'        
        sqlstr = "update identity set push_token = '" + p_token  + "' where id in ('"
        for i in range(4):
            sqlstr += self.idlist[i] 
            if i < 3:
                sqlstr += "', '"  
            else:
                sqlstr += "')"
        sqlList.append(sqlstr)  
        sqlstr = 'TRUNCATE notification_v2_identity_association'
        sqlList.append(sqlstr)  
        sqlstr = 'delete from notification_v2'
        sqlList.append(sqlstr)      
        dbConnect.dbSetting(test_parameter['db'], sqlList)    
        initdata.resetData(test_parameter['db'], self.idlist[0]) 
        # 取消追蹤
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
        T.SetTracking(header, 'delete', self.idlist[0])
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        T.SetTracking(header, 'delete', self.idlist[0])
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        T.SetTracking(header, 'delete', self.idlist[0])    
        #設定追蹤
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        T.SetTracking(header, 'post', self.idlist[0])
        
    def teardown_class(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # 清除動態
        res = api.get_photo_list(test_parameter['prefix'], header, self.idlist[0], '20', '1')   
        if res.status_code == 200:
            res1 = json.loads(res.text)
            photo_list = res1['data']        
        for i in photo_list:        
            res = api.operator_photopost(test_parameter['prefix'], header, 'delete', str(i['id']), '')
        # 取消黑名單
        res = api.delete_block_user(test_parameter['prefix'], header, self.idlist[3])
    
    def sendPostGift(self):
        sqlStr = "select id, point, name from gift where category_id = 108 and status = 1"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        giftId = result[0][0]
        point = result[0][1]
        name = result[0][2]
        print('create')
        photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], test_parameter['photo_url'], 3)
        print('get photo')
        photoId = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], self.idlist[2])
        print('send gift')
        photo.sendPhotoGift(test_parameter['user1_token'], test_parameter['user1_nonce'], test_parameter['prefix'], photoId[0], giftId)
        return(point, giftId, name, photoId[0])

    def testFanstracking(self):
        # 給直播主，但會依粉絲身份判斷link是個人頁還是名片頁        
        # common    
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        T.SetTracking(header, 'post', self.idlist[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        res = T.GetMessage(self.idlist[0], header, 1)
        restext = json.loads(res.text)
        print(restext)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'TRACK_MASTER_REQUEST'
        assert restext['data'][0]['content'] == '追蹤了你'
        assert restext['data'][0]['link'] == '/user/' + self.idlist[3]
        # livemaster
        time.sleep(1)        
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']    
        T.SetTracking(header, 'post', self.idlist[0])
        res = T.GetMessage(self.idlist[0], header, 2)        
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'TRACK_MASTER_REQUEST'
        assert restext['data'][0]['content'] == '追蹤了你'
        assert restext['data'][0]['link'] == '/liveMaster/' + self.idlist[1]
        assert restext['data'][0]['createAt'] > restext['data'][1]['createAt']
        # black黑名單
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']        
        body = {'userId' : self.idlist[3]}  
        res = api.add_block_user(test_parameter['prefix'], header, body)   
        
    def testPhoto(self):
        # 給粉絲，所以要判斷黑名單
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']       
        body = {'photoPath': test_parameter['photo_url'],  'content': 'test123'} 
        api.add_photopost(test_parameter['prefix'], header, body)
        res = api.get_photo_list(test_parameter['prefix'], header, self.idlist[0], '20', '1')
        restext = json.loads(res.text)  
        pid = str(restext['data'][0]['id'])
        # 檢查不在黑名單的粉絲會收到通知
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']            
        res = T.GetMessage(self.idlist[2], header, 1)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'MASTER_POST_PHOTO'
        assert restext['data'][0]['content'] == '在初樂與你分享他的生活'
        assert restext['data'][0]['link'] == '/post/' + str(pid)
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']       
        res = T.GetMessage(self.idlist[1], header, 1)
        restext = json.loads(res.text)
        print(166)
        pprint(restext)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'MASTER_POST_PHOTO'
        assert restext['data'][0]['content'] == '在初樂與你分享他的生活'
        assert restext['data'][0]['link'] == '/post/' + str(pid)
        # 檢查在黑名單的粉絲不會收到通知
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']            
        res = T.GetMessage(self.idlist[3], header, 1)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0        
               
    def testComment(self):
        # 給直播主，但轉跳到該則動態
        # action = comment_reply_to_user
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        res = api.get_photo_list(test_parameter['prefix'], header, self.idlist[0], '20', '1')
        if res.status_code == 200:
            res1 = json.loads(res.text)           
            pid = str(res1['data'][0]['id'])
            header['X-Auth-Token'] = test_parameter['user_token']
            header['X-Auth-Nonce'] = test_parameter['user_nonce']
            comment = '粉絲新增動態評論-一般使用者'
            res = api.add_photo_comment(test_parameter['prefix'], header, pid, comment)  
            time.sleep(1)
            header['X-Auth-Token'] = test_parameter['broadcaster1_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
            comment = '粉絲新增動態評論-直播主'
            res = api.add_photo_comment(test_parameter['prefix'], header, pid, comment)  
        res = T.GetMessage(self.idlist[0], header, 2)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'COMMENT_REPLY_TO_USER'
        assert restext['data'][0]['content'] == '留言給你'
        assert restext['data'][0]['link'] == '/post/' + str(pid)
        assert restext['data'][0]['createAt'] > restext['data'][1]['createAt']
        assert restext['data'][1]['action'] == 'COMMENT_REPLY_TO_USER'
        assert restext['data'][1]['content'] == '留言給你'
        assert restext['data'][1]['link'] == '/post/' + str(pid)
    
    def testPostGift(self):
        # 給直播主，但轉跳到該則動態
        # action = comment_reply_to_user
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        result = self.sendPostGift()
        res = T.GetMessage(self.idlist[0], header, 2)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'MASTER_PHOTO_RECEIVE_GIFT'
        assert restext['data'][0]['content'] == '送了' + result[2] + '給你的動態'
        assert restext['data'][0]['link'] == '/post/' + str(result[3])
        assert restext['data'][0]['createAt'] > restext['data'][1]['createAt']
     
    def testOpenroom(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        rid = sundry.Openroom(test_parameter['prefix'], header, 5, False, 0, '608行開播', 5)
        print('rid = %d'%rid)
        # 檢查不在黑名單的粉絲會收到通知
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']            
        res = T.GetMessage(self.idlist[2], header, 1)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'MASTER_ON_LIVE'
        assert restext['data'][0]['content'] == '熱烈開播中，快來支持你最愛的他！'
        assert restext['data'][0]['link'] == '/room/' + str(rid)
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']   
        print('toke=%s'%header['X-Auth-Token'])    
        res = T.GetMessage(self.idlist[1], header, 1)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['action'] == 'MASTER_ON_LIVE'
        assert restext['data'][0]['content'] == '熱烈開播中，快來支持你最愛的他！'
        assert restext['data'][0]['link'] == '/room/' + str(rid)
        # 檢查在黑名單的粉絲不會收到通知
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']            
        res = T.GetMessage(self.idlist[3], header, 1)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0        
        
    
