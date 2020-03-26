import time
import json
from ..assistence import api
from ..assistence import initdata
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

class TestliveComment():    
    def test_add_comment(self):
        '''
        1.指定不存在的post id
        2.token/nonce不存在
        '''
        pass

    def test_get_comment(self):
        '''
        1.指定不存在的post id(200，data沒有值且totalcount=0)
        2.指定正確的post id(200). 
        '''
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
        body = {'photoPath': test_parameter['photo_url'],  'content': 'test123'} 
        api.add_photopost(test_parameter['prefix'], header, body)
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header) 
        res = api.get_photo_list(test_parameter['prefix'], header, mid, '10', '1')
        restext = json.loads(res.text)
        pid = str(restext['data'][0]['id'])

        #---------create new comment---------#
        for i in range(10):
            comment = '動態評論' + str(i)
            res = api.add_photo_comment(test_parameter['prefix'], header, pid, comment)  
            assert int(res.status_code / 100) == 2

        res = api.get_comment_list(test_parameter['prefix'], header, pid, '5', '1')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 5
        assert restext['totalCount'] == 10
        assert restext['data'][0]['createAt'] >= restext['data'][1]['createAt']

        res = api.get_comment_list(test_parameter['prefix'], header, pid, '3', '2')
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 200
        assert len(restext['data']) == 3
        assert restext['totalCount'] == 10
        assert restext['data'][0]['comment'] == '動態評論6'

        res = api.get_comment_list(test_parameter['prefix'], header, '0', '5', '1')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0
        assert restext['totalCount'] == 0

        
    def test_delete_comment(self):
        '''
        1.指定不存在的comment id(404)
        2.token/nonce不存在(401)
        3.指定正確的comment id(200)
        4.一般使用者不可刪除comment()
        5.直播主不可刪除非自己動態的comment()
        '''
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header) 
        res = api.get_photo_list(test_parameter['prefix'], header, mid, '10', '1')
        restext = json.loads(res.text)
        #pprint(restext)
        pid = str(restext['data'][0]['id'])
        res = api.get_comment_list(test_parameter['prefix'], header, pid, '5', '1')
        restext = json.loads(res.text)
        cid = str(restext['data'][0]['id'])

        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        res = api.delete_comment(test_parameter['prefix'], header, pid, cid)
        assert res.status_code == 401
    
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']   
        res = api.delete_comment(test_parameter['prefix'], header, pid, cid)
        assert res.status_code == 404

        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']   
        res = api.delete_comment(test_parameter['prefix'], header, pid, cid)
        assert res.status_code == 403

        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
        res = api.delete_comment(test_parameter['prefix'], header, pid, cid)
        assert res.status_code == 200

        res = api.delete_comment(test_parameter['prefix'], header, pid, cid)
        assert res.status_code == 404

        res = api.get_comment_list(test_parameter['prefix'], header, pid, '5', '1')
        restext = json.loads(res.text)
        assert restext['data'][0]['id'] != int(cid)
