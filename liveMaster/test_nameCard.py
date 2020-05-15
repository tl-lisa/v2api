import time
import json
import datetime
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
cards = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
cover_list = ['https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/460d7772e0ec11e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/7922266ce69111e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/118161eae8d911e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/8b640c78e8da11e9beff42010a8c0fcc']

def setup_module():
    initdata.set_test_data(env, test_parameter)    

def teardown_module():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header) 
    #reset namecard
    res = api.namecard_operator(test_parameter['prefix'], header, 'get', mid,'')
    result1 = json.loads(res.text)
    for i in result1['data']['nameCard']['cards']:
        api.del_cover(test_parameter['prefix'], header, i['id'])

class TestnameCard():
    def test_add_cover(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
    # 新增前3筆資料皆可成功，第4筆會返回錯誤
        for i in range(4):
            res = api.namecard_operator(test_parameter['prefix'], header, 'post', uid, cover_list[i])        
            result1 = json.loads(res.text)
        # pprint(result1)
            if i < 3:
                assert res.status_code // 100 == 2
                cards.append(result1['data']['cards'][i])
            else:
                assert res.status_code// 100 == 4

    def test_change_cover(self):
        header1 = {'Content-Type': 'application/json', 'Connection': 'Keep-alive',
                'X-Auth-Token': test_parameter['broadcaster1_token'],
                'X-Auth-Nonce': test_parameter['broadcaster1_nonce']}
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # A直播主去修改B直播主的cover
        res = api.update_cover(test_parameter['prefix'], header1, cards[1]['id'])
        assert res.status_code // 100 == 2
        # 直播主自己指定正確的cover
        res = api.update_cover(test_parameter['prefix'], header, cards[1]['id'])
        assert res.status_code // 100 == 2
        # 確認cover設定是否正確
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        res = api.namecard_operator(test_parameter['prefix'], header, 'get', uid,'')
        result1 = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert result1['data']['nameCard']['cards'][1]['id'] == result1['data']['nameCard']['cover']
        # 指定不存在的cover number
        #pprint(cards)
        res = api.update_cover(test_parameter['prefix'], header, 0)
        assert res.status_code // 100 == 4

    def test_delete_cover(self):
        header1 = {'Content-Type': 'application/json', 'Connection': 'Keep-alive',
                'X-Auth-Token': test_parameter['broadcaster1_token'],
                'X-Auth-Nonce': test_parameter['broadcaster1_nonce']}
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # A直播主刪B直播主的namecard
        res = api.del_cover(test_parameter['prefix'], header1, cards[0]['id'])
        msg = json.loads(res.text)
        assert msg['Status'] == 'Error'
        assert msg['Message'] == 'Permission is required.'
        for i in cards:
            # 刪除存在的namecard
            res = api.del_cover(test_parameter['prefix'], header, i['id'])
            assert res.status_code // 100 == 2
            # 刪除不存在的namecard
            res = api.del_cover(test_parameter['prefix'], header, i['id'])
            assert res.status_code // 100 == 4


class TestnamecardLike():    
    user_header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    user1_header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    broad_header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    broad1_header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    totalLike = 0
    uid = ''
    mid = ''
    mid2 = ''

    def setup_class(self):
        # set header
        self.user_header['X-Auth-Token'] = test_parameter['user_token']
        self.user_header['X-Auth-Nonce'] = test_parameter['user_nonce']
        #print('token = %s' % test_parameter['user_token'])
        self.user1_header['X-Auth-Token'] = test_parameter['user1_token']
        self.user1_header['X-Auth-Nonce'] = test_parameter['user1_nonce']
        self.broad_header['X-Auth-Token'] = test_parameter['broadcaster_token']
        self.broad_header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        self.broad1_header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        self.broad1_header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']       
        # 取得原始like數
        self.mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], self.broad_header)
        self.mid2 = api.search_user(test_parameter['prefix'], test_parameter['broadcaster2_acc'], self.broad_header)        
        self.uid = api.search_user(test_parameter['prefix'], test_parameter['user_acc'], self.broad_header)
        res = api.namecard_operator(test_parameter['prefix'], self.broad_header, 'get', self.mid,'')
        result1 = json.loads(res.text)
        self.totalLike = result1['data']['photoLikeCount']
    
    def teardown_class(self): 
        strSql = 'delete from profile_like'
        dbConnect.dbSetting(test_parameter['db'], strSql)

    def test_setlike_uidnotexist(self):
        # uid不存在       
        res = api.set_namecard_like(test_parameter['prefix'], self.broad_header, '1234EERR', 1000)
        assert res.status_code == 404

    def test_setlike_uidiscommon(self):    
        # uid為粉絲
        res = api.set_namecard_like(test_parameter['prefix'], self.user_header, self.uid, 1000)
        json_result = json.loads(res.text)
        assert json_result['Message'] == 'User is not LiveMaster.'
        assert json_result['Status'] == 'Error'

    def test_setlike_likemorethan1000(self):
        # uid為直播主,like數大於1000以1000計      
        res = api.set_namecard_like(test_parameter['prefix'], self.user_header, self.mid, 1001)
        assert res.status_code //100 == 2
        res = api.namecard_operator(test_parameter['prefix'], self.user_header, 'get', self.mid, None)
        result1 = json.loads(res.text)  
        assert result1['data']['photoLikeCount'] == self.totalLike + 1000 
        assert result1['data']['liked'] == True

    def test_setlike_correctcase(self):
        # uid為直播主,且like數恰為1000;有cacsh 5秒
        like_num = 1000
        res = api.set_namecard_like(test_parameter['prefix'], self.user_header, self.mid, like_num)
        assert res.status_code // 100 == 2
        time.sleep(5)
        res = api.namecard_operator(test_parameter['prefix'], self.user_header, 'get', self.mid,'')
        result1 = json.loads(res.text)
        assert result1['data']['photoLikeCount'] == self.totalLike + 2000         
    
    def test_getlike_nonamecard(self):
        #未設profile的get不應有問題
        res = api.namecard_operator(test_parameter['prefix'], self.user_header, 'get', self.mid2,'')
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 200
        assert restext['data']['liked'] == False

    def test_setlike_nonamecard(self):
        #未設profile送出like不會有問題
        res = api.set_namecard_like(test_parameter['prefix'], self.user1_header, self.mid2, 100)
        assert res.status_code == 200
