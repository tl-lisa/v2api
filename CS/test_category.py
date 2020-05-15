import json
import requests
import pymysql
import time
import string
from assistence import chatlib
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass   

class TestSupportcategory():
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        body = {'label': 'test category 123'}
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    
    def teardown_class(self):
        sqlList = ['delete from issue_category where id > 5', 'ALTER TABLE issue_category AUTO_INCREMENT = 6']
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def testAddcategory_case1(self):
        #POST api/v2/cs/supportCategory
        #正常case；sort值與id值預設相同
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        lableName = 'test add category'
        body = {'label': lableName}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code == 200
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        count = restext['totalCount']
        assert len(restext['data']) == count
        assert restext['data'][count - 1]['id'] == count
        assert restext['data'][count - 1]['label'] == lableName
        assert restext['data'][count - 1]['sort'] == count  

    def testAddcategory_case2(self):
        #資料不完整
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        body = {'label': None}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert int(res.status_code / 100) == 4
    
    def testAddcategory_case3(self):
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/supportCategory'
        body = {'label': '1234'}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert int(res.status_code / 100) == 4

    def testAddcategory_case4(self):
        #權限不對
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        apiName = '/api/v2/cs/supportCategory'
        lableName = 'test add category'
        body = {'label': lableName}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert int(res.status_code / 100) == 4

    def testEditcategory_case1(self):
        #PUT api/v2/cs/supportCategory/{{category ID}}
        #修改lable
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']        
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']        
        apiName = '/api/v2/cs/supportCategory/' + str(count) 
        lableName = 'test edit category'
        body = {'label': lableName}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert res.status_code == 200        
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        assert len(restext['data']) == count
        assert restext['data'][count - 1]['label'] == lableName
    
    def testEditcategory_case2(self):
        #修改sort
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        apiName = '/api/v2/cs/supportCategory/' + str(count - 1) 
        lableName = 'test edit category2 and sort'
        sort = 99
        body = {'label': lableName, 'sort': sort}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert res.status_code == 200
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        assert len(restext['data']) == count
        assert restext['data'][count - 1]['id'] == count - 1
        assert restext['data'][count - 1]['label'] == lableName
        assert restext['data'][count - 1]['sort'] == 99  
        assert restext['data'][count - 2]['id'] == count

    def testEditcategory_case3(self):
        #修改的id不存在
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory/' + str(0)
        lableName = 'test edit category'
        body = {'label': lableName}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4
    
    def testEditcategory_case4(self):
        #json格試錯誤
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        header['Content-Type'] = 'application/json'
        apiName = '/api/v2/cs/supportCategory/' + str(count - 1) 
        body = {}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditcategory_case5(self):
        #修改時token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/supportCategory/' + str(0)        
        lableName = 'test edit category'
        body = {'label': lableName}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testDeletecategory_case1(self):
        #DELETE api/v2/cs/supportCategory/{{category ID}}
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/supportCategory/' + str(count)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        assert int(res.status_code / 100) == 4
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert len(restext['data']) == count

    def testDeletecategory_case2(self):
        #刪除未被使用的category
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        count = restext['totalCount']
        apiName1 = apiName + '/' + str(count - 1) 
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'delete', None)
        assert res.status_code == 200
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)        
        restext = json.loads(res.text)
        pprint(612)
        pprint(restext)
        assert len(restext['data']) == count - 1

    def testDeletecategory_case3(self):
        #刪除不存在的category
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory/' + str(0) 
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        assert int(res.status_code / 100) == 4

    def testDeletecategory_case4(self):
        #刪除被使用的category
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/supportCategory/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
        #pprint(str(res.text))
        assert int(res.status_code / 100) == 4

    def testGetcategory_case1(self):
        #一般user可取得意見分類
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        apiName = '/api/v2/cs/supportCategory'  
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 2

    def testGetcategory_case2(self):
        #直播主可取得意見分類
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        apiName = '/api/v2/cs/supportCategory'  
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 2

    def testGetcategory_case3(self):
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/supportCategory/'  
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4
