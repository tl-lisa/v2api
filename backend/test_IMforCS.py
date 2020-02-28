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
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController2_acc'], header))


def teardown_module():
    pass


class TestcreateMessage():
    emptyBody = {}
    def setup_class(self):
        initdata.resetData(test_parameter['db'], idList[0])

    def createBody(self, valuesList):
        parameterList = ['receiver', 'sender', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']
        for i in range (len(valuesList)):
            self.emptyBody[parameterList[i]] = valuesList [i]
        return self.emptyBody

    def testSendText(self):
        # 正確權限及資料（文字）；接收者為一般user;場控發送      
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[2], idList[4], 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testSendPicture(self):
        # 正確權限及資料（圖片）；接收者為直播主；admin發送
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']             
        valuesList.extend([idList[0], idList[1], 'image', '', test_parameter['photo_url'], '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testSendVideo(self):
        # 正確權限及資料（影片）
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        valuesList.extend([idList[3], idList[4], 'video', '', '', test_parameter['preview_url'], test_parameter['video_url']])   
        body = self.createBody(valuesList)
        time.sleep(2)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testSendAgain(self):
        # 正確權限及資料（影片）
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[3], idList[4], 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        time.sleep(2)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 2

    def testWithoutAuth(self):
        # 權限不正確
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[2], idList[0], 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testReciverNotExist(self):
        # 接收者uid不存在
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend(['adobie1223-1239910239fddj', idList[4], 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testTypeAndSendTypeNotMatch(self):
        # 訊息類別與傳送類別不吻合
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        content = '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
        valuesList.extend([idList[2], idList[4], 'image', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testContentTextOver500(self):
        # 文字訊息超出限制
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        content = 'Test text over 500。'
        while 1:
            content += '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 ' 
            if len(content) > 500:
                break
        valuesList.extend([idList[2], idList[4], 'text', content, '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testTypeNotExist(self):    
        # 輸入非定義的訊息類別
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        valuesList.extend([idList[2], idList[4], 'picture', '', test_parameter['photo_url'], '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testWithoutContext(self):
        # 未傳入訊息
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        valuesList.extend([idList[2], idList[4], 'text', '', '', '', ''])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4

    def testWithoutPreviewUrl(self):
        # 傳影片但未帶入預覽圖
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']             
        valuesList.extend([idList[2], idList[4], 'vedio', '', '', '', test_parameter['photo_url']])   
        body = self.createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == 4


class TestgetDialoglist():
    MsgTimeList = []
    def testGetSendList(self):        
        # 查詢已傳送過訊息的user
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[4])
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        print('at 202 api=%s'%apiName)
        for i in restext['data']:
            self.MsgTimeList.append(i['latestMsgTime'])
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[3]
        assert restext['data'][1]['userId'] == idList[2]
    
    def testNotSendBy(self):
        # 查詢未傳送或接收訊息的user
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[5])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0
    
    def testTimeInRange(self):
        # 以時間做查詢條件
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[4])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[0]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']              
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        print('at 232 apiName = %s' % apiName)      
        pprint(restext)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 1
        assert restext['data'][0]['userId'] == idList[3]
        assert restext['data'][0]['latestMsgTime'] == self.MsgTimeList[0]

    def testTimeOutofRange(self):
        # 不在時間區間內
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[4])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0] - 10))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[0] - 5))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

    def testWithoutUUID(self):
        # 傳入的參數有誤（未給UUID）
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('userId={uid}&', '')
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[0]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']            
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4
    
    def testWithoutAuth(self):
        # 一般user資訊雖然正確，但不允許操作
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[2])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']              
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4
    
    def testSetting(self):
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&item=1&page=1'
        apiName = apiName.replace('{uid}', idList[4])
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[3]
        assert restext['data'][0]['latestMsgTime'] == self.MsgTimeList[0]
        assert len(restext['data']) == 1
        apiName = apiName.replace('page=1', 'page=2')
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[2]
        assert restext['data'][0]['latestMsgTime'] == self.MsgTimeList[1]
        assert len(restext['data']) == 1

class TestgetDialogueDetail():
    dialogList = []
    MsgTimeList = []
    def setup_class(self):
        apiName = '/api/v2/backend/instantMessage/roomList?userId={uid}&item=10&page=1'
        apiName = apiName.replace('{uid}', idList[4])
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        for i in restext['data']:
            self.dialogList.append(i['dialogId'])
            self.MsgTimeList.append(i['latestMsgTime'])
        self.MsgTimeList.sort()

    def testGetExistDialogueID(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{id}', self.dialogList[0])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        print('at 323 api = %s' % apiName)
        pprint(restext)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][1]['sender']['id'] == idList[4]
        assert restext['data'][1]['receiver']['id'] == idList[3]
        assert restext['data'][1]['msgType'] == 'video'
        assert restext['data'][1]['previewUrl'] == test_parameter['preview_url']
        assert restext['data'][1]['videoUrl'] == test_parameter['video_url']   

    def testGetNotExistDialogueID(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{id}', '0')
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

    def testSetting(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=1&page=1'
        apiName = apiName.replace('{id}', self.dialogList[0])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        print('at 353; api = %s' % apiName)
        pprint(restext)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['sender']['id'] == idList[4]
        assert restext['data'][0]['receiver']['id'] == idList[3]
        assert restext['data'][0]['msgType'] == 'text'
        assert restext['data'][0]['textContent'] == '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 '
        apiName = apiName.replace('page=1', 'page=2')
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['sender']['id'] == idList[4]
        assert restext['data'][0]['receiver']['id'] == idList[3]
        assert restext['data'][0]['msgType'] == 'video'
        assert restext['data'][0]['previewUrl'] == test_parameter['preview_url']
        assert restext['data'][0]['videoUrl'] == test_parameter['video_url']   

    def testWithoutAuth(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=1&page=1'
        apiName = apiName.replace('{id}', self.dialogList[0])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4
    
    def testWithoutDialogueID(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=1&page=1'
        apiName = apiName.replace('dialogId={id}&', '')
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[0]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4
    
    def testByTimeInRange(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{id}', self.dialogList[0])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[1]))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1]))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 1
        assert restext['data'][0]['sender']['id'] == idList[4]
        assert restext['data'][0]['receiver']['id'] == idList[3]
        assert restext['data'][0]['msgType'] == 'text'
        assert restext['data'][0]['textContent'] == '哈囉，你好。這裡是Truelove客服。收到你的問題，會儘快處理⋯⋯請耐心等待😄😄😄 '
    
    def testByTimeOutofRange(self):
        apiName = '/api/v2/backend/instantMessage/history?dialogId={id}&startTime={stime}&endTime={etime}&item=10&page=1'
        apiName = apiName.replace('{id}', self.dialogList[0])
        apiName = apiName.replace('{stime}', str(self.MsgTimeList[1] + 5))
        apiName = apiName.replace('{etime}', str(self.MsgTimeList[1] + 10))
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0
