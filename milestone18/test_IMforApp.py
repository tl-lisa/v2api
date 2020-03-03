#mileston18 IM要判斷黑名單，直播主不會取到黑名單的聊天室，但user被黑仍可發訊息#757
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
createTime = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def createBody(valuesList):
    emptyBody = {}
    parameterList = ['receiver', 'origin', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']
    for i in range (len(valuesList)):
        emptyBody[parameterList[i]] = valuesList[i]
    return emptyBody


def createMessage(recevier, sender, header, msgtype, content, photo_url, preview_url, video_url):
        valuesList = []
        apiName = '/api/v2/backend/instantMessage'
        valuesList.extend([recevier, sender, msgtype, content, photo_url, preview_url, video_url])           
        body = createBody(valuesList)
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)


def setup_module():
    Auth = []
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))    
    initdata.resetData(test_parameter['db'], idList[0])
    Auth.extend([test_parameter['backend_token'], test_parameter['backend_nonce'], test_parameter['liveController1_token'], test_parameter['liveController1_nonce']])
    for i in range(2):       
        header['X-Auth-Token'] = Auth[i * 2]
        header['X-Auth-Nonce'] = Auth[i * 2 + 1]   
        createMessage(idList[0], idList[i + 1], header, 'text', '哈囉，你好。這裡是Truelove客服。我們仍在處理中，請再等一下 ', '', '', '')
        createMessage(idList[3], idList[i + 1], header, 'text', '哈囉，你好。這裡是Truelove客服。我們仍在處理中，請再等一下 ', '', '', '')
        time.sleep(0.5)
        createMessage(idList[0], idList[i + 1], header, 'video', '', '', test_parameter['preview_url'], test_parameter['video_url'])
        createMessage(idList[3], idList[i + 1], header, 'video', '', '', test_parameter['preview_url'], test_parameter['video_url'])


def teardown_module():
    changelist = [] 
    changelist.append(idList[0]) 
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
    api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主


class TestgetRoomList():
    dialogIdList = []
    def testGetRoomList(self):        
        # 取得自己的聊天室清單（該帳號已有聊天室）
        apiName = '/api/v2/identity/instantMessage/roomList?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[2]
        assert restext['data'][1]['userId'] == idList[1]
        for i in restext['data']:
            self.dialogIdList.append(i['dialogId'])
    
    def testCheckAuth(self):
        # 取得自己的聊天室清單（該帳號尚無聊天室）
        apiName = '/api/v2/identity/instantMessage/roomList?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

    def testSetting(self):
        # 驗證取得的資料筆數是否依照item及page的設定
        apiName = '/api/v2/identity/instantMessage/roomList?item=1&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[2]
        assert restext['data'][0]['latestMsg'] == '對方傳送了影片'
        apiName = apiName.replace('page=1', 'page=2')
        #print(apiName)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 2
        assert restext['data'][0]['userId'] == idList[1]
        assert restext['data'][0]['latestMsg'] == '對方傳送了影片'

    def testCreateRoomOver7days(self):        
        # 聊天室建立時間超過7天，查詢時應仍存在
        sqlList = []
        UpdateDatetime = datetime.fromtimestamp(int(time.time())) - timedelta(days=8)
        sqlList.append("update dialog set create_at = '" + UpdateDatetime.strftime('%Y-%m-%d %H:%M:%S') + "' where id = '" + self.dialogIdList[0] + "'")
        apiName = '/api/v2/identity/instantMessage/roomList?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == len(self.dialogIdList)
    

class TestBlack():
    def testBlacklist(self):
        #直播主將user加入黑名單後，直播主看不到該聊天室；但user可以看到
        pass


class TestcreateMessage():
    def updatePoint(self, point, id):
        sqlList = []
        sqlList.append("update remain_points set remain_points = " + str(point) + " where identity_id = '" + id + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def getExperience(self, conditionStr):
        result = dbConnect.dbQuery(test_parameter['db'], conditionStr)
        return result

    def testUserSendMessageToCS(self):
        # 發送訊息給CS，不應該扣點；經驗值不會增加
        valuesList = []
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[2] + "', '" + idList[3]  + "')"     
        bfExperience = self.getExperience(sqlStr)
        self.updatePoint(0, idList[3])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '快點唄，反應很慢喲'   
        valuesList.extend([idList[2], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2
        afExperience = self.getExperience(sqlStr)
        for i in range(2):
            assert bfExperience[i] == afExperience[i]

    def testUserSendPicture(self):
        # 發送訊息圖檔
        valuesList = []
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        valuesList.extend([idList[2], '', 'image', '', test_parameter['photo_url'], '', ''])   
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2

    def testUserSendvideo(self):
        # 發送訊息影音檔
        valuesList = []
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        valuesList.extend([idList[2], '', 'video', '', '', test_parameter['preview_url'], test_parameter['video_url']])   
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2

    def testUserSendMessageWithoutRoom(self):
        # 一般使用者傳送的聊天室不存在；會失敗
        valuesList = []
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']    
        valuesList.extend([idList[2], '', 'image', '', test_parameter['photo_url'], '', ''])   
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 4

    def testCSSendMessageWithoutRoom(self):
        # 聊天室不存在，會自動建立聊天室
        pass

    def testCSSendMessageToUser(self):
        # CS傳訊息給user不應扣點
        valuesList = []
        self.updatePoint(0, idList[2])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']    
        content = '快點唄，反應很慢喲'   
        valuesList.extend([idList[3], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2
    
    def testCSSendToLive(self):
        #官方場控送訊息給直播主不應該會被扣點
        valuesList = []
        self.updatePoint(0, idList[2])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']    
        content = '官方場控傳訊息給直播主'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2

    def testAdminSendToLive(self):
        #經營者送訊息給直播主不應該會被扣點
        valuesList = []
        self.updatePoint(0, idList[2])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']    
        content = '系統經營傳訊息給直播主'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 2
    
class TestgetHistory():   
    dialogIdList = []
    def setup_class(self):
        apiName = '/api/v2/identity/instantMessage/roomList?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        for i in restext['data']:
            self.dialogIdList.append(i['dialogId'])
    
    def teardown_class(self):
        changelist = []
        changelist.append(idList[3])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '5') #轉回一般用戶

    def testGetExistDialogueID(self):
        #取得合法的聊天資訊
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['data'][0]['createAt'] >= restext['data'][1]['createAt']
        assert restext['data'][0]['sender'] == idList[1]
        assert restext['data'][0]['receiver'] == idList[3]
        assert restext['data'][0]['msgType'] == 'video'
        assert restext['data'][0]['previewUrl'] == test_parameter['preview_url']
        assert restext['data'][0]['videoUrl'] == test_parameter['video_url']

    def testGetNotExistDialogueID(self):
        #傳入的聊天室不存在
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        apiName = apiName.replace('{id}', '0')
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4        
        
    def testSetting(self):
        #驗證回傳的資料筆數是否符合設定
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=1&page=1'
        apiName = apiName.replace('{id}', self.dialogIdList[1])
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 3
        apiName = apiName.replace('page=1', 'page=2')
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert len(restext['data']) == 1
        assert restext['totalCount'] == 3
        
    def testWithoutAuth(self):
        #不能取得非本人的聊天資訊
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=1&page=1'
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        header['X-Auth-Token'] = test_parameter['user1_token']
        header['X-Auth-Nonce'] = test_parameter['user1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4
    
    def testWithoutDialogueID(self):
        #傳入的參數不正確
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=1&page=1'
        apiName = apiName.replace('dialogId={id}&', '')
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        assert res.status_code // 100 == 4

    def testHistoryTalkWithCS(self):
        # 與客服的訊息不限時間
        sqlList = []
        changelist = []
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        UpdateDatetime = datetime.fromtimestamp(int(time.time())) - timedelta(days=366)
        sqlList.append("update instant_message set create_at = '" + UpdateDatetime.strftime('%Y-%m-%d %H:%M:%S') + "' where dialog_id = '" + self.dialogIdList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        print(apiName)
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 6
        changelist.append(idList[3])
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉成直播主
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 6
    

    def testCSGetOverhalfYear(self):
        # 客服可取得半年內的資料
        sqlList = []
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        UpdateDatetime = datetime.fromtimestamp(int(time.time())) - timedelta(days=183)
        sqlList.append("update instant_message set create_at = '" + UpdateDatetime.strftime('%Y-%m-%d %H:%M:%S') + "' where dialog_id = '" + self.dialogIdList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 6
        sqlList.clear()
        UpdateDatetime = datetime.fromtimestamp(int(time.time())) - timedelta(days=184)
        sqlList.append("update instant_message set create_at = '" + UpdateDatetime.strftime('%Y-%m-%d %H:%M:%S') + "' where dialog_id = '" + self.dialogIdList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

    def testGetHistoryAgain(self):
        #傳完訊息後再取得一次資訊
        valuesList = []
        time.sleep(1)
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['liveController1_token']
        header['X-Auth-Nonce'] = test_parameter['liveController1_nonce']
        content = '我是sender' + datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')  
        valuesList.extend([idList[3], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)   
        assert res.status_code // 100 == 2
        valuesList.clear() 
        time.sleep(1)
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content1 = '我是receiver' + datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')  
        valuesList.extend([idList[2], '', 'text', content1, '', '', ''])       
        body = createBody(valuesList)
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        assert res.status_code // 100 == 2
        time.sleep(1)   
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)     
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 8
        assert restext['data'][0]['createAt'] > restext['data'][1]['createAt']
        assert restext['data'][0]['sender'] == idList[3]
        assert restext['data'][0]['receiver'] == idList[2]
        assert restext['data'][0]['msgType'] == 'text'
        assert restext['data'][0]['textContent'] == content1    
        assert restext['data'][1]['sender'] == idList[2]
        assert restext['data'][1]['receiver'] == idList[3]
        assert restext['data'][1]['msgType'] == 'text'
        assert restext['data'][1]['textContent'] == content

class TestMessageToLiveMaster():
    dialogIdList = []

    def updatePoint(self, point, id):
        sqlList = []
        sqlList.append("update remain_points set remain_points = " + str(point) + " where identity_id = '" + id + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def getDBData(self, conditionStr):
        result = dbConnect.dbQuery(test_parameter['db'], conditionStr)
        return result

    def getHistoy(self):
        apiName = '/api/v2/identity/instantMessage/roomList?item=10&page=1'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        for i in restext['data']:
            self.dialogIdList.append(i['dialogId'])

    def setup_class(self):
        valuesList = []
        apiName = '/api/v2/liveMaster/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']             
        content = '哈囉，歡迎到Truelove新天地。來看看我的直播😄😄😄 ' 
        valuesList.extend([idList[3], 'giftGiversToSendIM', 'text', content, '', '', ''])   
        body = createBody(valuesList)  
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    
    def teardown_class(self):
        changelist = [] 
        changelist.append(idList[0]) 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主
    
    def testUserSendMessageToLive(self):
        # 發送訊息給LiveMaster，應該扣點；經驗值增加(user+20*3; livemaster+20)
        valuesList = []
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[0] + "', '" + idList[3]  + "') order by identity_id"     
        bfExperience = self.getDBData(sqlStr)
        self.updatePoint(20, idList[3])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '哈囉大主播，我是你的小粉1號'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        pprint(body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        restest = json.loads(res.text)   
        assert res.status_code // 100 == 2
        assert restest['data']['pointLeft'] == 0
        afExperience = self.getDBData(sqlStr)
        for i in range(2):
            if bfExperience[i][1] == idList[0]:
                assert afExperience[i][0] - bfExperience[i][0] == 20
            else:
                assert afExperience[i][0] - bfExperience[i][0] == 60

    def testUserSendMessagWithoutPoint(self):
        # user傳送訊息時已無點數可扣;訊息傳送會失敗
        valuesList = []
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '哈囉大主播，你好哇。。。怎麼都不回我？'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)       
        assert res.status_code // 100 == 4
   
    def testLiveMasterSendMessageToUser(self):
        # 直播主傳訊息給user不應扣點
        valuesList = []
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[0] + "', '" + idList[3]  + "') order by identity_id"     
        bfExperience = self.getDBData(sqlStr)
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
        content = '哈囉小粉1號....歡迎'   
        valuesList.extend([idList[3], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        restest = json.loads(res.text)   
        assert res.status_code // 100 == 2
        assert restest['data']['pointLeft'] == 0
        afExperience = self.getDBData(sqlStr)
        for i in range(2):
            assert afExperience[i] == bfExperience[i]

    def testLiveMasterBlackUser(self):
        # 直播主封鎖該名user,該user仍可傳訊息
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId' : idList[3]}  
        api.add_block_user(test_parameter['prefix'], header, body)
        valuesList = []
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[0] + "', '" + idList[3]  + "') order by identity_id"     
        bfExperience = self.getDBData(sqlStr)
        self.updatePoint(20, idList[3])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '哈囉大主播，我是你的小粉1號'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        restest = json.loads(res.text)   
        assert res.status_code // 100 == 2
        assert restest['data']['pointLeft'] == 0
        afExperience = self.getDBData(sqlStr)
        for i in range(2):
            if bfExperience[i][1] == idList[0]:
                assert afExperience[i][0] - bfExperience[i][0] == 20
            else:
                assert afExperience[i][0] - bfExperience[i][0] == 60

    def testUserSendTwiceToLive(self):
        # 發送訊息給LiveMaster，應該扣點；經驗值增加(user+20*3; livemaster+20)
        valuesList = []
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[0] + "', '" + idList[3]  + "') order by identity_id"     
        bfExperience = self.getDBData(sqlStr)
        self.updatePoint(40, idList[3])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '哈囉大主播，我是你的小粉1號'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        res1 = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        sqlStr = "select remain_points from remain_points where identity_id = '" + idList[3] + "'"
        remainPoints = self.getDBData(sqlStr)
        if (res.status_code // 100 == 2) and (res1.status_code // 100 == 2):
            assert remainPoints[0][0] == 0
        else:
            assert remainPoints[0][0] == 20
        sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idList[0] + "', '" + idList[3]  + "') order by identity_id"     
        afExperience = self.getDBData(sqlStr)
        if (res.status_code // 100 == 2) and (res1.status_code // 100 == 2):
            for i in range(2):
                if bfExperience[i][1] == idList[0]:
                    assert afExperience[i][0] - bfExperience[i][0] == 40
                else:
                    assert afExperience[i][0] - bfExperience[i][0] == 120
        else:
            for i in range(2):
                if bfExperience[i][1] == idList[0]:
                    assert afExperience[i][0] - bfExperience[i][0] == 20
                else:
                    assert afExperience[i][0] - bfExperience[i][0] == 60

    def testLivemasterChangeToUser(self):
        # 直播主轉成一般user;列表會顯示，但無法互傳訊息
        changelist = [] 
        valuesList = []    
        changelist.append(idList[0]) 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        api.change_roles(test_parameter['prefix'], header, changelist, '5') #轉成一般用戶
        self.updatePoint(20, idList[3])
        apiName = '/api/v2/identity/instantMessage'
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']    
        content = '哈囉大主播，我是你的小粉1號'   
        valuesList.extend([idList[0], '', 'text', content, '', '', ''])       
        body = createBody(valuesList)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)    
        assert res.status_code // 100 == 4
    
    def testMasterWithUserOnly7day(self):
        #超過7天的訊息即不會撈出
        sqlList = []
        self.getHistoy()
        apiName = '/api/v2/identity/instantMessage/history?dialogId={id}&item=10&page=1'
        UpdateDatetime = datetime.fromtimestamp(int(time.time())) - timedelta(days=8)
        sqlList.append("update instant_message set create_at = '" + UpdateDatetime.strftime('%Y-%m-%d %H:%M:%S') + "' where dialog_id = '" + self.dialogIdList[0] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = apiName.replace('{id}', self.dialogIdList[0])
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']      
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)       
        restext = json.loads(res.text)
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

    
    