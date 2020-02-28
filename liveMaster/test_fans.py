import time
import json 
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    

def teardown_module():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    mid1 = api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header)
    #reset tracking status
    header['X-Auth-Token'] = test_parameter['user_token']
    header['X-Auth-Nonce'] = test_parameter['user_nonce']  
    res = api.set_tracking(test_parameter['prefix'], header, 'delete', mid1)  
    if res.status_code != 200:
        pprint(res.text) 

class TestfansAndblack():
    def test_get_fans_list(self):
        '''
        1.依uid取得粉絲清單，與token/nonce無關
        2.每頁筆數符合設定值
        3.粉絲數應與namecard相符
        '''
        fans = []
        fans1 = []
        #print('get fans list')
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']   
        mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header) 
        mid1 = api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header) 
        uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header) 

        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']  
        res = api.set_tracking(test_parameter['prefix'], header, 'post', mid)
        res = api.set_tracking(test_parameter['prefix'], header, 'post', mid1)    

        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']   
        res = api.get_fans_list(test_parameter['prefix'], header, mid1, '50', '1')
        mid1_list = json.loads(res.text)
        assert res.status_code == 200
        assert len(mid1_list['data']) <= 50
        for i in mid1_list['data']:
            fans1.append(i['id'])
        assert uid in fans1

        res = api.get_fans_list(test_parameter['prefix'], header, mid, '50', '1')
        mid_list = json.loads(res.text)
        assert res.status_code == 200
        assert len(mid_list['data']) <= 50
        for i in mid_list['data']:
            fans.append(i['id'])
        assert uid in fans

        fans.clear()
        fans1.clear()
        mid_list.clear()
        mid1_list.clear()

        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']  
        res = api.set_tracking(test_parameter['prefix'], header, 'delete', mid)
        assert res.status_code == 200

        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']   
        res = api.get_fans_list(test_parameter['prefix'], header, mid1, '50', '1')
        mid1_list = json.loads(res.text)    
        assert res.status_code == 200
        assert len(mid1_list['data']) <= 50
        for i in mid1_list['data']:
            fans1.append(i['id'])
        assert uid in fans1

        res = api.get_fans_list(test_parameter['prefix'], header, mid, '50', '1')
        mid_list = json.loads(res.text)
        assert res.status_code == 200
        assert len(mid_list['data']) <= 50
        for i in mid_list['data']:
            fans.append(i['id'])
        assert uid not in fans

        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        res = api.namecard_operator(test_parameter['prefix'], header, 'get', uid,'')
        result1 = json.loads(res.text)
        totalLike = result1['data']['fansCount']
        assert len(mid_list['data']) == totalLike

