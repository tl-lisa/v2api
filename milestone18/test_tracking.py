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

class TestTracking():
    idlist = [] 
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))        
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header)) 
        initdata.resetData(test_parameter['db'], self.idlist[0])
        #加入動態 
        array1 = [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['broadcaster_acc'], 
                test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], test_parameter['broadcaster1_acc']]  
        for i in range(2):
            header['X-Auth-Token'] = array1[i * 3]
            header['X-Auth-Nonce'] = array1[i * 3 + 1]
            content = '我是' + array1[i * 3 + 2] + '的動態'
            body = {'photoPath': test_parameter['photo_url'],  'content': content} 
            #res = api.add_photopost(test_parameter['prefix'], header, body)
            api.add_photopost(test_parameter['prefix'], header, body)
            #print(res.text)
            time.sleep(1)
        
    def teardown_class(self):
        # 清除動態
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        res = api.get_photo_list(test_parameter['prefix'], header, self.idlist[0], '20', '1')   
        if res.status_code == 200:
            res1 = json.loads(res.text)
            photo_list = res1['data']        
        for i in photo_list:        
            res = api.operator_photopost(test_parameter['prefix'], header, 'delete', str(i['id']), '')
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
        res = api.get_photo_list(test_parameter['prefix'], header, self.idlist[1], '20', '1')   
        if res.status_code == 200:
            res1 = json.loads(res.text)
            photo_list = res1['data']        
        for i in photo_list:        
            res = api.operator_photopost(test_parameter['prefix'], header, 'delete', str(i['id']), '')    
        # 取消追蹤
        apilink = '/api/v2/identity/track/liveMaster?item=10&page=1'      
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            T.SetTracking(header, 'delete', i['id'])          
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        for i in restext['data']:
            T.SetTracking(header, 'delete', i['id'])          
    
    def testSetTracak(self):
        # 正常case
        for i in range(2):
            header['X-Auth-Token'] = test_parameter['user_token']
            header['X-Auth-Nonce'] = test_parameter['user_nonce']      
            res = T.SetTracking(header, 'post', self.idlist[i])
            assert res.status_code == 200
            header['X-Auth-Token'] = test_parameter['user1_token']
            header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
            res = T.SetTracking(header, 'post', self.idlist[i])
            assert res.status_code == 200            
        # token/nonce不存在        
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']      
        res = T.SetTracking(header, 'post', self.idlist[0])        
        assert int(res.status_code / 100) == 4          
        # 不存在的MasterId        
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = T.SetTracking(header, 'post', '12345678984')        
        assert int(res.status_code / 100) == 4
    
    def testGetTracklist(self):
        apilink = '/api/v2/identity/track/liveMaster?item=10&page=1'      
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        body = {'userId': self.idlist[3]}
        api.add_block_user(test_parameter['prefix'], header, body) 
        # 正常粉絲           
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        #pprint(restext)
        assert res.status_code == 200
        assert restext['data'][0]['id'] == self.idlist[1]
        assert restext['data'][1]['id'] == self.idlist[0]
        # 在黑名單的粉絲
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['id'] == self.idlist[1]
        # 從黑名單中移除
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.delete_block_user(test_parameter['prefix'], header, self.idlist[3])
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 1
        assert restext['data'][0]['id'] == self.idlist[1]
        time.sleep(5)
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['id'] == self.idlist[1]
        assert restext['data'][1]['id'] == self.idlist[0]
        #直撥主變成一般user
        bid = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        bid.append(self.idlist[0])
        api.change_roles(test_parameter['prefix'], header, bid, 5)   
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['id'] == self.idlist[1]                    
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        api.change_roles(test_parameter['prefix'], header, bid, 4)   

    def testGetOnairTracklist(self):
        header1 = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
        apilink = '/api/v2/identity/track/liveMaster?filter=onAir&item=10&page=1'
        # 加入黑名單
        header1['X-Auth-Token'] = test_parameter['broadcaster_token']
        header1['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        body = {'userId': self.idlist[3]}
        api.add_block_user(test_parameter['prefix'], header1, body)           
        sockinfo = api.get_load_balance(test_parameter['prefix'], header1)
        sip = sockinfo['socketIp']
        sport = int(sockinfo['socketPort'])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (sip, sport)
        sock.connect(server_address)
        chatlib.chat_room_auth(sock, header1)
        rid = chatlib.new_room(sock, 'Test tracker 250行')
        while 1:        
            header['X-Auth-Token'] = test_parameter['user_token']
            header['X-Auth-Nonce'] = test_parameter['user_nonce']           
            res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)        
            restext = json.loads(res.text)
            assert res.status_code == 200
            assert len(restext['data']) == 1        
            assert restext['data'][0]['id'] == self.idlist[0]
            header['X-Auth-Token'] = test_parameter['user1_token']
            header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
            res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
            restext = json.loads(res.text)
            assert res.status_code == 200
            #assert len(restext['data']) == 0
            # 取消黑名單
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
            api.delete_block_user(test_parameter['prefix'], header, self.idlist[3])
            time.sleep(3)    
            header['X-Auth-Token'] = test_parameter['user1_token']
            header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
            res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
            restext = json.loads(res.text)
            assert res.status_code == 200
            assert len(restext['data']) == 0
            time.sleep(2)
            res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
            restext = json.loads(res.text)
            assert res.status_code == 200
            assert restext['data'][0]['id'] == self.idlist[0]
            break
        chatlib.leave_room(rid, sock)           
        
    def testGetPhotoTracklist(self):
        apilink = '/api/v2/identity/track/photoPost?item=10&page=1'
        body = {'userId': self.idlist[3]}
        # 加入黑名單
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.add_block_user(test_parameter['prefix'], header, body)   
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        #print(restext)
        assert res.status_code == 200
        assert restext['data'][0]['content'] == '我是' + test_parameter['broadcaster1_acc'] + '的動態'
        assert restext['data'][0]['owner']['id'] == self.idlist[1]    
        assert restext['data'][0]['giftPoints'] == 0
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['content'] == '我是' + test_parameter['broadcaster1_acc'] + '的動態'
        assert restext['data'][0]['owner']['id'] == self.idlist[1]
        assert restext['data'][1]['content'] == '我是' + test_parameter['broadcaster_acc'] + '的動態'
        assert restext['data'][1]['owner']['id'] == self.idlist[0]
        assert restext['data'][0]['giftPoints'] == 0
        # 取消黑名單
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.delete_block_user(test_parameter['prefix'], header,  self.idlist[3])
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 1    
        time.sleep(30)
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['content'] == '我是' + test_parameter['broadcaster1_acc'] + '的動態'
        assert restext['data'][0]['owner']['id'] == self.idlist[1]
        assert restext['data'][1]['content'] == '我是' + test_parameter['broadcaster_acc'] + '的動態'
        assert restext['data'][1]['owner']['id'] == self.idlist[0]
        assert restext['data'][0]['giftPoints'] == 0
        #直撥主變成一般user
        bid = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        bid.append(self.idlist[0])
        api.change_roles(test_parameter['prefix'], header, bid, 5)   
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
        res = api.apiFunction(test_parameter['prefix'], header, apilink, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['content'] == '我是' + test_parameter['broadcaster1_acc'] + '的動態'
        assert restext['data'][0]['owner']['id'] == self.idlist[1]
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        api.change_roles(test_parameter['prefix'], header, bid, 4)   

    def testDelTracak(self):
        #正常刪除
        for i in range(2):
            header['X-Auth-Token'] = test_parameter['user_token']
            header['X-Auth-Nonce'] = test_parameter['user_nonce']      
            res = T.SetTracking(header, 'delete', self.idlist[i])
            assert res.status_code == 200
            header['X-Auth-Token'] = test_parameter['user1_token']
            header['X-Auth-Nonce'] = test_parameter['user1_nonce']                  
            res = T.SetTracking(header, 'delete', self.idlist[i])        
            assert res.status_code == 200            
        # token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']      
        res = T.SetTracking(header, 'delete', self.idlist[0])        
        assert int(res.status_code / 100) == 4          
        # 不存在的MasterId
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = T.SetTracking(header, 'delete', '123456789')
        assert int(res.status_code / 100) == 4        