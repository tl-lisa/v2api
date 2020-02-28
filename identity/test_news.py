import json
import requests
import pymysql
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    

def teardown_module():
    pass   


class TestAnnounce():    
    def createAnnounce(self, title, content, dep, tag, uLevel, uType):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']           
        apilink = '/api/v2/backend/announcement/'
        body = {
                'title': title,
                'content': content,
                'department': dep,
                'tag': tag,
                'userLevel': uLevel,
                'userType': uType
            }
        api.apiFunction(test_parameter['prefix'], header, apilink, 'post', body)   
        return

    idlist = [] 
    dep = ['customer_service', 'planning', 'product'] 
    def setup_class(self):
        sqlList = []
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))        
        self.idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))        
        getLinkAddr = '/api/v2/backend/announcement/list?item=1000&page=1'
        delLinkaddr = '/api/v2/backend/announcement/{announcementid}'   
        res = api.apiFunction(test_parameter['prefix'], header, getLinkAddr, 'get', '')
        restext = json.loads(res.text)
        for i in restext['data']:
            linkAddr = delLinkaddr.replace('{announcementid}', str(i['id']))
            res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'delete', '')
        #update token
        sqlstr = "update identity set push_token = '" +  "' where id in ('"
        for i in range(4):
            sqlstr += self.idlist[i] 
            if i < 3:
                sqlstr += "', '"  
            else:
                sqlstr += "')"
        sqlList.append(sqlstr)  
        dbConnect.dbSetting(test_parameter['db'], sqlList)     

    def teardown_class(self):
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        getLinkAddr = '/api/v2/backend/announcement/list?item=1000&page=1'
        delLinkaddr = '/api/v2/backend/announcement/{announcementid}'   
        res = api.apiFunction(test_parameter['prefix'], header, getLinkAddr, 'get', '')
        restext = json.loads(res.text)
        for i in restext['data']:
            linkAddr = delLinkaddr.replace('{announcementid}', str(i['id']))
            res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'delete', '')
    
    def testGetAnnouncelist(self):
        #取得公告列表
        self.createAnnounce('Only for users', '針對一般使用者公告', self.dep[0], 6, [], 'common')        
        apilink = '/api/v2/identity/{user id}/announcement/list?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        linkAddr = apilink.replace('{user id}',self.idlist[2])
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data'][0]['title'] == 'Only for users'
        assert restext['data'][0]['content'] == '針對一般使用者公告'
        assert restext['data'][0]['source']['department'] == self.dep[0]
        #無公告列表
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']                  
        linkAddr = apilink.replace('{user id}', self.idlist[0])
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert len(restext['data']) == 0
        #不存在的token/nonce
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']                  
        linkAddr = apilink.replace('{user id}', self.idlist[2])
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4
        #錯誤的userid
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        linkAddr = apilink.replace('{user id}', '12345687')
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')        
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code / 100) == 2
        assert restext['totalCount'] == 0
    
    def testGetSingelAnnounce(self):
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']                  
        apilink = '/api/v2/identity/{user id}/announcement/list?item=10&page=1'
        linkAddr = apilink.replace('{user id}',self.idlist[2])
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        id = restext['data'][0]['id']
        #取得正確資料
        linkAddr = '/api/v2/identity/announcement/' + str(id)
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert res.status_code == 200
        assert restext['data']['title'] == 'Only for users'
        assert restext['data']['content'] == '針對一般使用者公告'
        assert restext['data']['source']['department'] == self.dep[0]
        #給錯誤的id
        linkAddr = '/api/v2/identity/announcement/0'
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4
        #給不存在的token/nonce
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']                      
        linkAddr = '/api/v2/identity/announcement/'  + str(id)
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4
        #給正確的token/nonce，但這則公告不屬於我
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']                  
        linkAddr = '/api/v2/identity/announcement/'  + str(id)
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'get', '')
        restext = json.loads(res.text)
        assert int(res.status_code / 100) == 4    

