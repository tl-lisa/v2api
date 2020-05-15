import json
import requests
import time
import string
from assistence import api
from assistence import initdata
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass

class TesteditUserinfo():
    idlist = []
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        api.set_tracking(test_parameter['prefix'], header, 'post', self.idlist[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.set_tracking(test_parameter['prefix'], header, 'post', self.idlist[1])

    def teardown_class(self):
        body = {}
        body['identityStatus'] = 1
        body['phoneNumber'] = '0988'
        body['selfDesc'] = 'test'
        body['nickname'] = '1234'
        body['sexvalue'] = 0
        body['realName'] = 'wahaha'
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        header['X-Auth-Token'] = test_parameter['backend_token']
        api.backend_user(test_parameter['prefix'], header, body, self.idlist[0])
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        api.set_tracking(test_parameter['prefix'], header, 'delete', self.idlist[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        api.set_tracking(test_parameter['prefix'], header, 'delete', self.idlist[1])

    def testEdituserinfo_case1(self):
        #比對編輯後的資料
        apiName = '/api/v2/backend/user/'
        nickname = 'QATester'
        sexvalue = 1
        realName = 'QATester123'
        phone = '0988111111'
        desc = 'backend user update 😘😘😘😘'
        body = {'nickname': nickname, 'sex': sexvalue, 'realName': realName, 'phoneNumber': phone, 'selfDesc': desc}
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        header['X-Auth-Token'] = test_parameter['backend_token']
        apiName += self.idlist[2]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['nickname'] == nickname
        assert restext['sexValue'] == sexvalue
        assert restext['selfDesc'] == desc
        assert restext['realName'] == realName
        assert restext['phoneNumber'] == phone
        assert restext['identityStatus'] == 1

    def testEdituserinfo_case2(self):
        #有資料的欄位才會被update(含空白)
        apiName = '/api/v2/backend/user/'
        nickname = 'QATester321'
        sexvalue = 1
        realName = 'QATester123'
        phone = '0988111111'
        desc = ''
        body = {'nickname': nickname, 'selfDesc': desc}
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        header['X-Auth-Token'] = test_parameter['backend_token']
        apiName += self.idlist[2]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['nickname'] == nickname
        assert restext['sexValue'] == sexvalue
        assert restext['selfDesc'] == desc
        assert restext['realName'] == realName
        assert restext['phoneNumber'] == phone
        assert restext['identityStatus'] == 1

    def testEdituserinfo_case3(self):
        #一般user不能update
        apiName = '/api/v2/backend/user/'
        nickname = 'QATester321'
        body = {'nickname': nickname, 'selfDesc': ''}
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        apiName += self.idlist[2]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testEdituserinfo_case4(self):
        #userid不存在
        apiName = '/api/v2/backend/user/'
        nickname = 'QATester321'
        body = {'nickname': nickname, 'selfDesc': ''}
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        apiName += 'aaboiej12323jije'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testEdituserinfo_case5(self):
        #suspend後不能登入且，追蹤跟被追蹤都要清除
        apiName = '/api/v2/backend/user/'
        body = {'identityStatus': -2}
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        header['X-Auth-Token'] = test_parameter['backend_token']
        apiName += self.idlist[0]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert restext['identityStatus'] == -2
        res = api.user_login_1(test_parameter['prefix'], test_parameter['broadcaster_acc'], test_parameter['broadcaster_pass'])
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['nonce'] is None
        assert restext['token'] is None
        assert restext['errorCode'] == -35
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        res = api.get_fans_list(test_parameter['prefix'], header, self.idlist[1] , '10', '1')
        assert str(res).find(test_parameter['broadcaster_acc']) == -1
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        header['X-Auth-Token'] = test_parameter['user_token']
        apiName1 = '/api/v2/identity/track/liveMaster?item=999&page=1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'get', None)
        assert str(res).find(test_parameter['user_acc']) == -1        
