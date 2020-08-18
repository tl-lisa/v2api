import time
import json
from assistence import api
from assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    
    initdata.set_test_data(env, test_parameter)
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'] , 
    [test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idList)

def teardown_module():
    pass

class TestBlack():
    def test_case1(self):        
        #輸入正確的uuid
        #被黑該帳號無法搜尋到該直播主
        #被黑追蹤清單看不到該直播主
        #被黑粉絲清單不受影響
        #被黑直播主開播不會收到開播通知
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId' : idlist[2]}  
        res = api.add_block_user(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == 2
        res = api.get_block_user(test_parameter['prefix'], header, '10', '1')
        restext = json.loads(res.text)   
        assert res.status_code // 100 == 2
        assert restext['data'][0]['userId'] == idlist[2]
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce'] 
        body = {'liveMasterLoginId': 'api'}
        res = api.search_master(test_parameter['prefix'], header, body, '10', '0')
        restext = json.loads(res.text)    
        assert res.status_code // 100 == 2
        assert len(restext['liveMasters']) == 0

    def test_case2(self):
        #2.輸入不正確的uuid
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId' : '123459BB'}  
        res = api.add_block_user(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == 4

    def test_case3(self):
        #3.一般user無法新增black
        pass

    def test_case4(self):
        #4.在黑名單內無法在hotlive及newlive中找到該直播主(後補)
        pass

    def test_case5(self):
        #6.token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce'] 
        body = {'userId' : idlist[1]}  
        res = api.add_block_user(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == 4

    def test_case6(self):
        #7.json空值
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {}  
        res = api.add_block_user(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == 4

    def test_case7(self):
        #8.重複加入黑名單會回報錯誤
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId' : idlist[2]}  
        res = api.add_block_user(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == 4
    
    def test_case8(self):
        #9.一般場控可以加入black
        #print('add block')
        pass

    def test_case9(self):
        #10.官方場控不可加入黑名單
        pass

    def test_case10(self):
        #11.官方場控在直播間可以踢人
        pass

    def test_case11(self):
        #12.官方場控可以直接將一般用戶加入黑名單
        pass
    

class TestdeleteBlack():
    def test_case1(self):
        #token/nonce不正確會回（401）
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        res = api.delete_block_user(test_parameter['prefix'], header, idlist[2])
        assert res.status_code // 100 == 4

    def test_case2(self):
        #依token/nonce來判斷，解除屬於自己的黑名單
        #解除黑名單後，可搜尋到該直播主
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        res = api.get_block_user(test_parameter['prefix'], header, '10', '1')
        restext = json.loads(res.text)    
        assert res.status_code // 100 == 2
        assert restext['data'][0]['userId'] == idlist[2]
        for i in restext['data']:
            res = api.delete_block_user(test_parameter['prefix'], header, i['userId'])
            assert res.status_code // 100 == 2
        res = api.get_block_user(test_parameter['prefix'], header, '10', '1')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0
        assert restext['totalCount'] == 0 
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce'] 
        body = {'liveMasterLoginId': '1234'}
        res = api.search_master(test_parameter['prefix'], header, body, '10', '0')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['liveMasters'][0]['loginId'] == test_parameter['broadcaster_acc']

    def test_case3(self):
        #不在黑名單內可在hotlive及newlive中找到該直播主(後補)
        pass

    def test_case4(self):
        #輸入不正確的uuid應回(404)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        res = api.delete_block_user(test_parameter['prefix'], header, 'uid1234-QDAG2354')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 4
        assert restext['Message'] == 'User is not in blacklist.'
        
