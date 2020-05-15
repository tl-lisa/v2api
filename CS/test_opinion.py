import json
import requests
import pymysql
import time
import string
import threading
import socket
from assistence import chatlib
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass   


class T():
    @staticmethod
    def GetcsSupport(keyword, uid, tid, status, startT, endT, items, pages):
        apiName = []
        apiName.append('/api/v2/cs/support/list?keyword={{keyword}}&UUID={{UUID}}&category={{tag ID}}&status={{status}}&startTime={{startTime}}&endTime={{endTime}}&item={{item}}&page={{page}}')
        if keyword == '' or keyword is None:
            apiName.append(apiName[0].replace('keyword={{keyword}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{keyword}}', str(keyword)))
            del apiName[0]
        if uid == '' or uid is None:
            apiName.append(apiName[0].replace('UUID={{UUID}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{UUID}}', str(uid)))
            del apiName[0]
        if tid == '' or tid is None:
            apiName.append(apiName[0].replace('category={{tag ID}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{tag ID}}', str(tid)))
            del apiName[0]
        if status == '' or status is None:
            apiName.append(apiName[0].replace('status={{status}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{status}}', str(status)))
            del apiName[0]
        if startT == '' or startT is None:
            apiName.append(apiName[0].replace('startTime={{startTime}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{startTime}}', str(startT)))
            del apiName[0]
        if endT == '' or endT is None:
            apiName.append(apiName[0].replace('endTime={{endTime}}&', ''))
            del apiName[0]
        else:
            apiName.append(apiName[0].replace('{{endTime}}', str(endT)))
            del apiName[0]
        apiName.append(apiName[0].replace('{{item}}', str(items)))
        del apiName[0]
        apiName.append(apiName[0].replace('{{page}}', str(pages)))
        del apiName[0]   
        return apiName[0]

    @staticmethod
    def CreateSuggestion(title, content, category, files, platform, OSVersion, manufacturer, AppVersion, deviceMarketingName, header):
        apiNmae = '/api/v2/cs/support'
        body = {}
        if title is not None:
            body['title'] = title
        if content is not None:
            body['content'] = content
        if category is not None:
            body['category'] = category
        if  files is not None:
            body['files'] = files
        if  platform is not None:
            body['platform'] = platform 
        if  OSVersion is not None:
            body['OSVersion'] = OSVersion
        if  manufacturer is not None:
            body['manufacturer'] = manufacturer
        if  AppVersion is not None:
            body['AppVersion'] = AppVersion
        if  deviceMarketingName is not None:
            body['deviceMarketingName'] = deviceMarketingName
        pprint(body)
        res = api.apiFunction(test_parameter['prefix'], header, apiNmae, 'post', body)
        return res


class TestSupport():
    idlist = [] 
    def setup_class(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))        
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header)) 
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header)) 

    def teardown_class(self):        
        sqlList = ['delete from customer_issue where id > 1', 'alter table customer_issue AUTO_INCREMENT = 1'] 
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def testSendquestion_case1(self):
        #POST api/v2/cs/support
        #直播主&無上傳任何附檔
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        res = T.CreateSuggestion(' test ', 'QA test', 1, [], 'Android', '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)
        assert int(res.status_code / 100) == 2
    
    def testSendquestion_case2(self):
        #一般使用者&有上傳檔案
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        files = [test_parameter['photo_url'], test_parameter['photo_url'], test_parameter['photo_url']]
        res = T.CreateSuggestion('123test ', 'QA test 🤬🤬', 2, files, 'iOS', '12.4.3', 'Xiaomi', '1.7.5(29785aa)', 'iPhone 6s Plus', header)
        assert int(res.status_code / 100) == 2

    def testGetlist_case1(self):
        #token/nonce不存在        
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = T.GetcsSupport('test', None, None, '未處理', None, None, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testGetlist_case2(self):
        #一般user
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        apiName = T.GetcsSupport('test', None, None, '未處理', None, None, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testGetlist_case3(self):
        #篩選找不到資料
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = T.GetcsSupport('', None, None, 'test1234', None, None, 10, 1)
        #print('apiName = %s' %apiName)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testGetlist_case4(self):
        #用keyword找資料
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = T.GetcsSupport('test', '', '', '', '', '', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        for i in restext['data']:
            assert i['title'].find('test') >= 0
        assert restext['data'][0]['createAt'] > restext['data'][1]['createAt'] 

    def testGetlist_case5(self):
        #用uuid
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = T.GetcsSupport('', self.idlist[2], '', '', '', '', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        print(apiName)
        assert int(res.status_code / 100) == 2
        for i in restext['data']:
            assert i['user']['id'] == self.idlist[2]
            assert i['user']['loginId'] == test_parameter['user_acc']

    def testGetlist_case6(self):
        #category
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = T.GetcsSupport('', '', 1, '', '', '', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        for i in restext['data']:
            assert i['category'] == 1

    def testGetlist_case7(self):
        #status
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = T.GetcsSupport('', '', '', '處理', '', '', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code / 100) == 2
        for i in restext['data']:
            assert i['status'].find('處理') > 0
            if i['status'] == '未處理':
                assert i['staff']['id'] == ''
            else:
                assert i['staff']['id'] == self.idlist[4]

    def testGetlist_case8(self):
        #startTime&endTime
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        startTime = int(time.time()) - 1
        time.sleep(1)
        T.CreateSuggestion(' test ', 'QA test', 1, [], 'Android', '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)
        endTime = int(time.time()) 
        time.sleep(2)
        T.CreateSuggestion(' test4321 ', 'QA test', 1, [], 'Android', '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)
        apiName = T.GetcsSupport('', '', '', '', startTime, endTime, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2
        for i in restext['data']:
            assert i['title'] == ' test '
            assert i['createAt'] >= startTime
            assert i['createAt'] <= endTime

    def testGetlist_case9(self):
        #startTime&endTime
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        startTime = int(time.time()) - 60 * 60 * 24 * 7
        endTime = startTime + 3600
        apiName = T.GetcsSupport('', '', '', '', startTime, endTime, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)        
        restext = json.loads(res.text)
        pprint(apiName)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 0        

    def testGetlist_case10(self):
        #startTime&endTime
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        startTime = int(time.time()) - 60 * 60 * 24 * 7
        endTime = '你23353'
        apiName = T.GetcsSupport('', '', '', '', startTime, endTime, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)        
        restext = json.loads(res.text)
        pprint(apiName)
        assert int(res.status_code / 100) == 2
        assert len(restext['data']) == 0        

    def testGetlist_case11(self):
        #startTime&endTime
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        startTime = 1573574400000
        endTime = 1573801408677
        apiName = T.GetcsSupport('', '', '', '', startTime, endTime, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)        
        assert int(res.status_code / 100) == 4

    def testGetlist_case12(self):
        #正確資料
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        files = [test_parameter['photo_url']]
        T.CreateSuggestion(' test ', 'QA🥰', 1, files, 'Android', '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)    
        header['Content-Type'] = None    
        apiName = T.GetcsSupport('', None, None, '處理', None, None, 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)        
        restext = json.loads(res.text)
        print(apiName)
        pprint(restext)
        assert int(res.status_code / 100) == 2
        assert restext['data'][0]['title'] == ' test '
        assert restext['data'][0]['content'] == 'QA🥰'
        assert restext['data'][0]['category'] == 1
        assert restext['data'][0]['files'][0] == files[0]
        assert restext['data'][0]['platform'] == 'Android'
        assert restext['data'][0]['OSVersion'] == '9'
        assert restext['data'][0]['manufacturer'] == 'Xiaomi'
        assert restext['data'][0]['AppVersion'] == '1.5.1+225.20191021'
        assert restext['data'][0]['deviceMarketingName'] == 'Redmi 7'
        assert restext['data'][0]['user']['loginId'] == test_parameter['backend_acc']

    def testGetspecial_case1(self):
        #問題id不存在
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        apiName = '/api/v2/cs/support/0'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testGetspecial_case2(self):
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testGetspecial_case3(self):
        #一般user
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case1(self):
        #PUT /v2/cs/support/{{question id}}
        #id不存在
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {'Status': 'Ok'}
        apiName = '/api/v2/cs/support/0'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case2(self):
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        body = {'Status': 'Ok'}
        apiName = '/api/v2/cs/support/0'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case3(self):
        #權限不正確
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        body = {'Status': 'Ok'}
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case4(self):
        #status空白
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {'Status': '  '}
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case5(self):
        #status空值
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {'Status': ''}
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case6(self):
        #正確更改
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {'Status': 'Ok 【😀】'}
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4

    def testEditquestion_case7(self):
        #json error
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        body = {}
        apiName = '/api/v2/cs/support/1'
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'put', body)
        assert int(res.status_code / 100) == 4


    def testSendquestion_case4(self):
        #token/nonce不存在
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        res = T.CreateSuggestion('123test ', 'QA test', 1, [], 'Android', '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)
        assert int(res.status_code / 100) == 4

    def testSendquestion_case5(self):
        #json格式錯誤
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        res = T.CreateSuggestion('123test ', 'QA test', 1, [], None, '9', 'Xiaomi', '1.5.1+225.20191021', 'Redmi 7', header)
        assert int(res.status_code / 100) == 4
