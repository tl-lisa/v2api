#milestone24 動態評論禁詞，若是評論中有禁詞出現會整句吃掉不新增進DB #1309
import time
import json
import pytest
from assistence import api
from assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
cards = []
idList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'] , 
    [test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idList)
 
def getTestData(testType):
    testData = []
    if testType == 'addComment':
        #scenario, token, nonce, desc, expecte; 驗證auth及photo id不存在的狀況
        testData = [
            ('broadcaster add comment', 'broadcaster_token', 'broadcaster_nonce', 'broadcaster add comment', 2),
            ('broadcaster1 add comment', 'broadcaster1_token', 'broadcaster1_nonce', 'broadcaster1 add comment', 2),
            ('livecontroller1 add comment', 'liveController1_token', 'liveController1_nonce', 'livecontroller 1add comment', 2),
            ('backend user add comment', 'backend_token', 'backend_nonce', 'backend user add comment', 2),
            ('user add comment', 'user_token', 'user_nonce', 'user add comment', 2),
            ('user add comment', 'user_token', 'user_nonce', 'user add forbidden words 代儲', 2),
            ('user1 add comment', 'user1_token', 'user1_nonce', 'user1 add comment', 2),
            ('pid not exist', 'user1_token', 'user1_nonce', 'user1 add comment', 4),
            ('auth wrong', 'err_token', 'err_nonce', '', 4)
        ]
    elif testType == 'getComment':
        #scenario, token, nonce, blackId, suspendedId, item, page, expected, totalCount
        #除停權，黑名單的comment不可撈出，其餘任何人皆可讀取該名直播主的動態評論
        testData = [
            ('broadcaster get comment', 'broadcaster_token', 'broadcaster_nonce', -1, -1, 5, 1, 2, 6),
            ('broadcaster1 get comment', 'broadcaster1_token', 'broadcaster1_nonce', -1, -1, 5, 2, 2, 6),
            ('livecontroller1 get comment', 'liveController1_token', 'liveController1_nonce', -1, -1, 5, 1, 2, 6),
            ('backend user get comment', 'backend_token', 'backend_nonce', -1, -1, 5, 1, 2, 6),
            ('user get comment', 'user_token', 'user_nonce', -1, -1, 5, 1, 2, 6),
            ('user1 get comment', 'user1_token', 'user1_nonce', -1, -1, 5, 1, 2, 6),
            ('auth wrong', 'err_token', 'err_nonce', -1, -1, 5, 1, 2, 6), #之前小馬說不限。請TPM在評估無token/nonce的人是否可以任意撈取資料。目前暫訂可以撈
            #('black user', 'backend_token', 'backend_nonce', 2, -1, 5, 1, 2, 5), skip this case. wait for PM discuss
            ('suspend user', 'backend_token', 'backend_nonce', -1, 3, 5, 1, 2, 5)
        ]
    elif testType == 'delComment':
        #scenario, token, nonce, cid, expected; 只有直播主可以刪除自己動能的評論，確認有處理comment id不存在的事件
        testData = [
            ('comment id not exist', 'broadcaster_token', 'broadcaster_nonce', '999', 4),
            ('broadcaster1 delete comment', 'broadcaster1_token', 'broadcaster1_nonce', '1', 4),
            ('livecontroller1 delete comment', 'liveController1_token', 'liveController1_nonce', '1', 4),
            ('backend user delete comment', 'backend_token', 'backend_nonce', '1', 4),
            ('user delete comment', 'user_token', 'user_nonce', '1', 4),
            ('broadcaster delete comment', 'broadcaster_token', 'broadcaster_nonce', '1', 2)
        ]
    return testData

class TestliveComment():    
    pid = ''
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
        body = {'photoPath': test_parameter['photo_url'],  'content': 'test123'} 
        api.add_photopost(test_parameter['prefix'], header, body)
        res = api.get_photo_list(test_parameter['prefix'], header, idList[0], '10', '1')
        restext = json.loads(res.text)
        pprint(restext)
        self.pid = str(restext['data'][0]['id'])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/backend/forbidden'
        body = {'word': '代儲'}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)

    def teardown_method(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        api.delete_block_user(test_parameter['prefix'], header, idList[2])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        api.change_user_mode(test_parameter['prefix'], idList[3], 1, header)

    @pytest.mark.parametrize("scenario, token, nonce, desc, expected", getTestData('addComment'))
    def test_add_comment(self, scenario, token, nonce, desc, expected):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce] 
        if scenario == 'pid not exist':
            pid = str(0)
        else:
            pid = self.pid
        res = api.add_photo_comment(test_parameter['prefix'], header, pid, desc)  
        assert res.status_code // 100 == expected

    @pytest.mark.parametrize("scenario, token, nonce, blackId, suspendedId, item, page, expected, totalCount", getTestData('getComment'))
    def test_get_comment(self, scenario, token, nonce, blackId, suspendedId, item, page, expected, totalCount):
        if blackId >= 0:
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
            api.add_block_user(test_parameter['prefix'], header, {'userId': idList[blackId]})
        if suspendedId >= 0:
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
            api.change_user_mode(test_parameter['prefix'], idList[suspendedId], -2, header)
        time.sleep(5)
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce] 
        res = api.get_comment_list(test_parameter['prefix'], header, self.pid, item, page)
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert len(restext['data']) <= item
            assert restext['totalCount'] == totalCount
            if page == 1:
                assert restext['data'][0]['createAt'] >= restext['data'][1]['createAt']
        if blackId >= 0:
            assert str(restext['data']).find(idList[blackId]) < 0
        if suspendedId >= 0:
            assert str(restext['data']).find(idList[suspendedId]) < 0
        
    @pytest.mark.parametrize("scenario, token, nonce, cid, expected", getTestData('delComment'))
    def test_delete_comment(self, scenario, token, nonce, cid, expected ):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce] 
        res = api.delete_comment(test_parameter['prefix'], header, self.pid, cid)
        assert res.status_code // 100 == expected
        if expected == 2:
            res = api.get_comment_list(test_parameter['prefix'], header, self.pid, '10', '1')
            restext = json.loads(res.text)
            isFound = False
            for i in restext['data']:
                if i['id'] == int(cid):
                    isFound = True
                    break
            assert isFound == False
