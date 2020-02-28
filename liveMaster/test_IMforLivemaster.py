import json
import requests
import time
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta


env = 'testing'
test_parameter = {}
idList = []
userList = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    initdata.resetData(test_parameter['db'], idList[0])
    for i in range(2000, 2030):
        account = 'track' + str(i)
        userList.append(api.search_user(test_parameter['prefix'], account, header))


def teardown_module():
    pass


class TestcreateMessage():
    emptyBody = {}
    def setup_class(self):
        sqlList = []    
        sqlList.append("update user_experience set experience = 25088 where identity_id = '" + idList[0] + "'")
        sqlList.append("update user_experience set experience = 0 where identity_id = '" + idList[1] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def createBody(self, valuesList):
        parameterList = ['receiver', 'origin', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']
        for i in range (len(valuesList)):
            self.emptyBody[parameterList[i]] = valuesList[i]
        return self.emptyBody

    def testSendText(self):
        # 正確權限及資料（文字）
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testSendPicture(self):
        # 正確權限及資料（圖片）；接收者為直播主；admin發送
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'image', '', test_parameter['photo_url'], '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testSendVideo(self):
        # 正確權限及資料（影片）
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'video', '', '', test_parameter['preview_url'], test_parameter['video_url']])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testWithoutAuth(self):
        # 權限不正確
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testReciverNotExist(self):
        # 接收者uid不存在
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend(['adobie1223-1239910239fddj', 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testTypeAndSendTypeNotMatch(self):
        # 訊息類別與傳送類別不吻合
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'image', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testContentTextOver500(self):
        # 文字訊息超出限制
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = 'Test text over 500。'
        while 1:
            content += '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
            if len(content) > 500:
                break
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testTypeNotExist(self):    
        # 輸入非定義的訊息類別
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'picture', '', test_parameter['photo_url'], '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testWithoutContext(self):
        # 未傳入訊息
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', '', '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testWithoutPreviewUrl(self):
        # 傳影片但未帶入預覽圖
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'vedio', '', '', '', test_parameter['photo_url']])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testLiveMasterLevelless10(self):
        # 直播主等級小於青銅10，不能傳訊息
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testOriginNotExist(self):
        # 管道來源錯誤
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], 'ToSendIM', 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testLiveMasterSendOver10_user(self):
        # 直播主每天最多僅發10筆給新的用戶
        valuesList = []
        sendCount = 0
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。歡迎到TrueLove，請追蹤我喲' 
        sqlStr = "select count(*) from quota_log where permission = 'new_users_to_send_im' and user_id = '" + idList[0] + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        sendCount = int(result[0][0])
        for i in range(11):
            valuesList.extend([userList[i], 'newUsersToSendIM', 'text', content, '', '', ''])   
            body = self.createBody(valuesList)
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            if sendCount < 10:
                assert res.status_code // 100 == 2
                sendCount += 1
            else:
                assert res.status_code // 100 == 4
                break
            valuesList.clear()

    def testLiveMasertSendOver10_giver(self):
        # 直播主每天最多僅發10筆給送禮的用戶
        valuesList = []
        sendCount = 0
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。謝謝你送的禮物 ' 
        sqlStr = "select count(*) from quota_log where permission = 'gift_givers_to_send_im' and user_id = '" + idList[0] + "'"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        sendCount = int(result[0][0])
        for i in range(10, 18):
            valuesList.extend([userList[i], 'giftGiversToSendIM', 'text', content, '', '', ''])   
            body = self.createBody(valuesList)
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
            if sendCount < 10:
                sendCount += 1
                assert res.status_code // 100 == 2
            else:
                assert res.status_code // 100 == 4
                break
            valuesList.clear()