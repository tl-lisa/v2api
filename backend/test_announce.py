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
    header['X-Auth-Token'] = test_parameter['cs_token']
    header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
    getLinkAddr = '/api/v2/backend/announcement/list?item=1000&page=1'
    delLinkaddr = '/api/v2/backend/announcement/{announcementid}'   
    res = api.apiFunction(test_parameter['prefix'], header, getLinkAddr, 'get', '')
    restext = json.loads(res.text)
    #print('26')
    #pprint(restext)
    for i in restext['data']:
        linkAddr = delLinkaddr.replace('{announcementid}', str(i['id']))
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'delete', '')


class T():
    @staticmethod
    def getAnnounceList(dep, item, page):
        linkAddr = '/api/v2/backend/announcement/list?dept=d1&item=t1&page=p1'
        if dep == '':
            linkAddr1 = linkAddr.replace('dept=d1&', '') 
        else:
            linkAddr1 = linkAddr.replace('d1', dep)        
        linkAddr1 = linkAddr1.replace('t1', str(item))
        linkAddr1 = linkAddr1.replace('p1', str(page))           
        return linkAddr1
    
    @staticmethod
    def createAnnounce(title, content, dep, tag, ulevel, utype, loginTime, regTime,pic,link,header):    
        body = {
            'title': title,
            'content': content,
            'department': dep,
            'tag': tag,
            'pictureUrl': pic,
            'link': link,
            'userLevel': ulevel,
            'userType': utype,
            'lastLoginPeriod': loginTime,
            'registerTimePeriod': regTime
        }    
        if loginTime == '':
            del body['lastLoginPeriod']
        if regTime == '':
            del body['registerTimePeriod']
        pprint(body) 
        linkAddr = '/api/v2/backend/announcement/'
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'post', body)
        return res       

class TestGetAnnounce():
    def testGetNone(self):
        #針對查無資料測試
        header['X-Auth-Token'] = test_parameter['project_token']
        header['X-Auth-Nonce'] = test_parameter['project_nonce']                          
        getLink = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, getLink, 'get', '')
        #restext = json.loads(res.text)
        assert int(res.status_code / 100) == 2

class TestCreateAnnounce():    
    dep = ['customer_service', 'planning', 'product'] 
    def testCreatenormalcase(self):
        #normal case: check all columns
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('NormalCase', 'Check all columns is correct', self.dep[0], 6, [], 'all', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod']['endTime'] == startTime + 120
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'NormalCase'
        assert len(restext['data'][0]['userLevel']) == 0
        assert restext['data'][0]['userType'] == 'all'

    def testUserlevelisnone(self):
        #user level is none
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('User level is none', 'Check all columns is correct', self.dep[0], 6, None, 'all', loginTime, regTime, pic, link, header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod']['endTime'] == startTime + 120
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'User level is none'
        assert restext['data'][0]['userLevel'] == []
        assert restext['data'][0]['userType'] == 'all'

    def testHasuserlevel(self):
        #Check user level
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('User level has data', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'common', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod']['endTime'] == startTime + 120
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'User level has data'
        assert restext['data'][0]['userLevel'] == ['diamond', 'niello']
        assert restext['data'][0]['userType'] == 'common'


    def testUsertypeiscommon(self):
        #User type is common
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Usertype=common', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'common', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod']['endTime'] == startTime + 120
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'Usertype=common'
        assert restext['data'][0]['userLevel'] == ['diamond', 'niello']
        assert restext['data'][0]['userType'] == 'common'

    def testUsertypeislivemaster(self):
        #User type is live_master
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Usertype=livemaster', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'live_master', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod']['endTime'] == startTime + 120
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'Usertype=livemaster'
        assert restext['data'][0]['userLevel'] == ['diamond', 'niello']
        assert restext['data'][0]['userType'] == 'live_master'

    def testUsertypeisempty(self):
        #User type is empty
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Usertype=empty', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], '', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 4
    
    def testUsertypeiswrong(self):
        #User type is empty
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Usertype=All', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'All', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 4

    def testLogintimeisnone(self):
        #login time is none
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('login time is none', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'live_master', None, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 2
        strAPI = T.getAnnounceList('', 10, 1)
        res = api.apiFunction(test_parameter['prefix'], header, strAPI, 'get', None)
        restext = json.loads(res.text)        
        assert restext['data'][0]['announcer']['id'] == api.search_user(test_parameter['prefix'], test_parameter['cs_acc'], header)
        assert restext['data'][0]['content'] == 'Check all columns is correct'
        assert restext['data'][0]['createAt'] >= startTime
        assert restext['data'][0]['department'] == 'customer_service'
        assert restext['data'][0]['lastLoginPeriod'] is None
        assert restext['data'][0]['link'] == link
        assert restext['data'][0]['pictureUrl'] == pic
        assert restext['data'][0]['registerTimePeriod']['startTime'] == startTime
        assert restext['data'][0]['tag']['id'] == 6
        assert restext['data'][0]['title'] == 'login time is none'
        assert restext['data'][0]['userLevel'] == ['diamond', 'niello']
        assert restext['data'][0]['userType'] == 'live_master'

def testLogintimeiswrong1(self):
        #Login time without endtime
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']   
        loginTime['startTime'] = startTime
        #loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Logintime is wrong-1', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'live_master', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 4

def testLogintimeiswrong2(self):
        #Login time without starttime
        pic = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/4c5f70eaf40011e9beff42010a8c0fcc.png'
        #pic1 = 'https://d3eq1e23ftm9f0.cloudfront.net/announcement/picture/c601c27af47f11e9beff42010a8c0fcc.png'
        link = 'https://truelovelive.com.tw:777'
        loginTime = {}
        regTime = {}
        startTime = int(time.time())
        header['X-Auth-Token'] = test_parameter['cs_token']
        header['X-Auth-Nonce'] = test_parameter['cs_nonce']           
        loginTime['endTime'] =  startTime + 120
        regTime['startTime'] = startTime
        regTime['endTime'] =  startTime + 120
        res = T.createAnnounce('Logintime is wrong-1', 'Check all columns is correct', self.dep[0], 6, ['diamond', 'niello'], 'live_master', loginTime, regTime,pic,link,header)        
        assert int(res.status_code / 100) == 4
