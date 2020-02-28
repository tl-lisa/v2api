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


class TestcoverNumber():
    userList = [] 
    startTime = int(time.time())
    levelList = []              #["bronze", "silver", "gold", "diamond", "niello"]        
    loginTime = {'startTime': startTime, 'endTime': startTime + 120}
    regTime = {'startTime': startTime, 'endTime': startTime + 120}
    
    def setup_class(self):      
        experience = [0, 1537090.91, 4623272.73, 34603636.36, 93818181.82] 
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']                      
        self.userList.append(api.search_user(test_parameter['prefix'], 'broadcaster100', header)) 
        self.userList.append(api.search_user(test_parameter['prefix'], 'broadcaster099', header)) 
        self.userList.append(api.search_user(test_parameter['prefix'], 'broadcaster098', header))         
        self.userList.append(api.search_user(test_parameter['prefix'], 'broadcaster097', header))         
        self.userList.append(api.search_user(test_parameter['prefix'], 'broadcaster096', header))         
        self.userList.append(api.search_user(test_parameter['prefix'], 'track0100', header)) 
        self.userList.append(api.search_user(test_parameter['prefix'], 'track0099', header))      
        self.userList.append(api.search_user(test_parameter['prefix'], 'track0098', header))         
        self.userList.append(api.search_user(test_parameter['prefix'], 'track0097', header))         
        self.userList.append(api.search_user(test_parameter['prefix'], 'track0096', header))     
        sqlList = []
        p_token = 'eUOePK4v6Xg:APA91bHqcnv2C7MSD9GMMTG2rs34cy4sVabpnNJ-hKqzjBzUHtWKHa84SRpZTQWDL7vX4b2tppZvFT25eXJerOVpBy_3xFWagcc6Z307JbJq'
        for i in range (len(self.userList)):
            j = i % 5
            sqlstr = "update user_experience set experience = " + str(experience[j]) + " where identity_id = '" + self.userList[i] + "'" 
            sqlList.append(sqlstr)
            sqlstr = "update identity set create_at = FROM_UNIXTIME(" + str(self.startTime + j * 20) + "), push_token = '" + p_token
            sqlstr += "', update_at = FROM_UNIXTIME(" + str(self.startTime + j * 25) + ") where id = '" + self.userList[i] + "'"  
            print(sqlstr)
            sqlList.append(sqlstr)   
        dbConnect.dbSetting(test_parameter['db'], sqlList)
         
    def teardown_class(self):
        '''
        sqlstr = 'update user_experience set experience = 0 where identity_id in ('
        for i in range(len(self.userList)):
            if (i == 0):
                sqlstr += "'"
            else:
                sqlstr += "','"
            sqlstr += self.userList[i]
        sqlstr += "')"
        '''
        self.userList.clear()

    def GetCovernumber(self, levelList, userType, loginTime, regTime):
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']                     
        linkAddr = '/api/v2/backend/announcement/coverage'
        body = {
    	    'userLevel': levelList,
    	    'userType': userType,
    	    'lastLoginPeriod': loginTime,
    	    'registerTimePeriod': regTime
        }        
        print(body)
        res = api.apiFunction(test_parameter['prefix'], header, linkAddr, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        return(restext)

    def testloginTime(self):
        #登入時間        
        checkText = self.GetCovernumber(self.levelList, 'all', self.loginTime, None)
        assert checkText['data']['totalCount'] == 10

    def testloginTimeandLevel(self):
        #登入時間 ＋ 等級
        self.levelList.append('silver')
        checkText = self.GetCovernumber(self.levelList, 'all', self.loginTime, None)
        assert checkText['data']['totalCount'] == 2
    
    def testloginTimeandType(self):
        #登入時間 ＋ type
        self.levelList.clear()
        checkText = self.GetCovernumber(self.levelList, 'common', self.loginTime, None)
        assert checkText['data']['totalCount'] == 5
        checkText = self.GetCovernumber(self.levelList, 'live_master', self.loginTime, None)
        assert checkText['data']['totalCount'] == 5

    def testregTime(self):
        #註冊時間
        checkText = self.GetCovernumber(self.levelList, 'all', None, self.regTime)
        assert checkText['data']['totalCount'] == 10    
    
    def testregTimeLevel(self):
        #註冊時間 ＋ 等級
        self.levelList.append('niello')
        checkText = self.GetCovernumber(self.levelList, 'all', None, self.regTime)
        assert checkText['data']['totalCount'] == 2  
    
    def testregTimeType(self):
        #註冊時間 ＋ type
        self.levelList.clear()
        checkText = self.GetCovernumber(self.levelList, 'common', None, self.regTime)
        assert checkText['data']['totalCount'] == 5    
        checkText = self.GetCovernumber(self.levelList, 'live_master', None, self.regTime)
        assert checkText['data']['totalCount'] == 5 

    def testloginTimeregTime(self):   
        #登入時間 ＋ 註刪時間
        loginTime1 = {'startTime': self.startTime + 20, 'endTime': self.startTime + 60}
        regTime1 = {'startTime': self.startTime, 'endTime': self.startTime + 50}
        checkText = self.GetCovernumber(self.levelList, 'all', loginTime1, regTime1)
        assert checkText['data']['totalCount'] == 4   
