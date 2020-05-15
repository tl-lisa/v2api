#coding = utf-8
import time
import json
from assistence import api
from assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
cards = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    

def teardown_module():
    pass    

class TestliveController(): 
    def test_add_liveController(self):
        '''
        1.直播主可以新增自己的場控
        2.輸入錯的uuid（404）
        3.錯誤的token/nonce（401）
        4.json格式錯誤
        5.輸入重複的uuid會擋掉(422)
        6.無論是一般用戶或是直播主，皆可設為場控
        註：順便測試取得liveController api
        '''
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        mid1 = api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header)   
        uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header) 
        
        body = {'userId' : uid}
        res = api.add_livecontroller(test_parameter['prefix'], header, body)
        assert res.status_code == 200
        body = {'userId' : mid1}
        res = api.add_livecontroller(test_parameter['prefix'], header, body)
        assert res.status_code == 200
    
        body = {'userId' : uid}
        res = api.add_livecontroller(test_parameter['prefix'], header, body)
        assert res.status_code == 422
            
        res = api.get_livecontroller(test_parameter['prefix'], header, mid, '5', '1')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['userId'] == uid
        assert len(restext['data']) == 2
        assert restext['totalCount'] == 2

        body = {'userId' : 'Abjowjefpr1234'}
        res = api.add_livecontroller(test_parameter['prefix'], header, body)        
        assert int(res.status_code / 100) == 4

        body = {}
        res = api.add_livecontroller(test_parameter['prefix'], header, body)
        assert res.status_code == 406


    def test_delete_liveController(self):
        '''
        1.直播主可以刪除自己的場控
        2.輸入錯的uuid（404）
        3.錯誤的token/nonce（401）
        4.直播主不可刪除非自己的場控（404）
        註：順便測試取得liveController api
        '''
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce'] 
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header) 
        res = api.delete_livecontroller(test_parameter['prefix'], header, uid)
        assert res.status_code == 404

        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        res = api.delete_livecontroller(test_parameter['prefix'], header, uid)
        assert res.status_code == 401

        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        res = api.delete_livecontroller(test_parameter['prefix'], header, 'UU1238-jdakda-123Dba')
        assert res.status_code == 404  

        res = api.get_livecontroller(test_parameter['prefix'], header, mid, '5', '1')
        restext = json.loads(res.text)
        #pprint(restext)
        assert res.status_code == 200
        assert restext['data'][0]['userId'] == uid
        assert len(restext['data']) == 2
        assert restext['totalCount'] == 2

        for i in restext['data']:
            res = api.delete_livecontroller(test_parameter['prefix'], header, i['userId'])
            assert res.status_code == 200

        res = api.get_livecontroller(test_parameter['prefix'], header, mid, '5', '1')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0
        assert restext['totalCount'] == 0

