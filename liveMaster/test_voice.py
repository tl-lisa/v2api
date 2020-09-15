#milestone29 加入vedio影音功能 #1882,1885,1887,1890(僅房主有權限編輯及管理)
import time
import json
import pytest
import websocket
from assistence import sundry
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import voicelib
from pprint import pprint

Msg = {
    200:{'Status': 'Ok', 'Message': 'SUCCESS'},
    401:{'Status': 'Error', 'Message': ['AUTH_ERROR', '使用者驗證錯誤，請重新登入']},
    403:{'Status': 'Error', 'Message': ['PERMISSION_REQUIRED', 'FORBIDDEN_TO_AUTH', '抱歉，您的使用權限不足！如有疑問，請洽初樂客服人員。']},
    400:{'Status': 'Error', 'Message': ['PARAM_TYPE_ERROR', 'LACK_OF_NECESSARY_PARAMS', 'DATA_EXISTED', 'REQUEST_DENIED']},
    406:{'Status': 'Error', 'Message': 'LACK_OF_NECESSARY_PARAMS'},
    404:{'Status': 'Error', 'Message': ['GIFT_CATAGORY_NOT_FOUND', 'MEDIA_NOT_FOUND', 'ROOM_NOT_FOUND', 'ADMIN_NOT_FOUND', 'USER_NOT_FOUND']}
}
env = 'QA'
DB = '35.234.17.150'
test_parameter = {}
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def createVoiceRoom(account):
    sqlStr   = "insert into sticker_group set name = 'smile', status = 1, created_at = '2020-06-30 19:21:32', "
    sqlStr  += "updated_at = '2020-06-30 19:21:32', create_user_id = 'lisa', update_user_id = 'lisa'"
    sqlStr1  = "insert into voice_chat_type set name = 'qa_test', background_image_url = 'http://yahoo.com.tw', "
    sqlStr1 += "sticker_group_id = 1, max_seats = 3, max_vip_seats = 1"  
    sqlList = [sqlStr, sqlStr1]
    dbConnect.dbSetting(DB, sqlList)
    header['X-Auth-Token'] = test_parameter['tl-lisa']['token']
    header['X-Auth-Nonce'] = test_parameter['tl-lisa']['nonce']
    apiName = '/api/v2/backend/voiceChat'
    body = {
        'typeId':1,
        'masterId': test_parameter[account]['id'],
        'title': account+'的直播間',
        'description': '快來加入'+account+'的直播間吧！',
        'password': '123456',
        'streamId':[
            'voiceChat_1_1',
            'voiceChat_1_2',
            'voiceChat_1_3'
        ]
    }
    api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    return 

def setup_module():
    initdata.get_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['tl-lisa']['token']
    header['X-Auth-Nonce'] = test_parameter['tl-lisa']['nonce']
    api.change_roles(test_parameter['prefix'], header, [test_parameter['broadcaster014']['id']], 4)


@pytest.fixture(scope="class")
def createInit():
    initdata.clearVoice(test_parameter['db'])
    sundry.clearCache(test_parameter['db'])
    for i in range(2):
        account = 'broadcaster01' + str(i)
        createVoiceRoom(account)

@pytest.fixture(scope="class")
def editInit():
    initdata.clearVoice(test_parameter['db'])
    sundry.clearCache(test_parameter['db'])
    for i in range(2):
        account = 'broadcaster01' + str(i)
        createVoiceRoom(account)
    header['X-Auth-Token'] = test_parameter['broadcaster011']['token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster011']['nonce']
    for i in range(12, 15):
        admin = 'broadcaster0' + str(i)
        apiName = '/api/v2/liveMaster/voiceChat/admin'
        body = {
            'roomId': 2,
            'userId': test_parameter[admin]['id']
        }
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
    apiName = '/api/v2/liveMaster/voiceChat/admin/2/' + test_parameter['broadcaster013']['id']
    api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
    header['X-Auth-Token'] = test_parameter['tl-lisa']['token']
    header['X-Auth-Nonce'] = test_parameter['tl-lisa']['nonce']
    api.change_roles(test_parameter['prefix'], header, [test_parameter['broadcaster014']['id']], 5)


def getTestData(funName):
    sqlStr = "select max(id) from voice_chat_room where status = 1"
    result = dbConnect.dbQuery(DB, sqlStr)
    vRoom = result[0][0]
    testData = []
    if funName == 'admin':
        #scenario, account, method, roomId, admin, adminList, expected
        testData = [
            ('僅房主可以新增管理員資料', 'broadcaster011', 'post', vRoom, 'broadcaster012', ['broadcaster012'],200),
            ('新增的管理員資料重複', 'broadcaster011', 'post', vRoom, 'broadcaster012', ['broadcaster012'], 400),
            ('一般user不可以新增管理員資料', 'track0010', 'post', vRoom, 'broadcaster013', ['broadcaster012'], 403),
            ('管理員不可以新增管理員資料', 'broadcaster012', 'post', vRoom, 'broadcaster013', ['broadcaster012'], 403),
            ('經營管理者不可以新增管理員資料', 'tl-lisa', 'post', vRoom, 'broadcaster013', ['broadcaster012'], 403),
            ('官方場控不可以新增管理員資料', 'lv000', 'post', vRoom, 'broadcaster013', ['broadcaster012'], 403),
            ('房間不存在卻要加管理員', 'broadcaster011', 'post', vRoom + 1, 'broadcaster013', ['broadcaster012'], 404),
            ('經營管理者不可為管理員', 'broadcaster011', 'post', vRoom, 'tl-lisa',['broadcaster012'],  404),
            ('官方場控不可為管理員', 'broadcaster011', 'post', vRoom, 'lv000', ['broadcaster012'], 404),
            ('一般user不可為管理員', 'broadcaster011', 'post', vRoom, 'track0010', ['broadcaster012'], 404),
            ('房主不可為管理員', 'broadcaster011', 'post', vRoom, 'broadcaster011', ['broadcaster012'], 400),
            ('他房房主可為管理員', 'broadcaster011', 'post', vRoom, 'broadcaster010', ['broadcaster010', 'broadcaster012'], 200),
            ('他房房主不可新增本房管理員', 'broadcaster010', 'post', vRoom, 'broadcaster013', ['broadcaster010', 'broadcaster012'], 403),
            ('非本房房主不可刪除本房管理員', 'broadcaster010', 'delete', vRoom, 'broadcaster010', ['broadcaster010', 'broadcaster012'], 403),
            ('經營管理者不可刪除本房管理員', 'tl-lisa', 'delete', vRoom, 'broadcaster010', ['broadcaster010', 'broadcaster012'], 403),
            ('官方場控不可刪除本房管理員', 'lv000', 'delete', vRoom, 'broadcaster010', ['broadcaster010', 'broadcaster012'], 403),
            ('刪除不存在的管理員', 'broadcaster011', 'delete', vRoom, 'broadcaster010', ['broadcaster010', 'broadcaster012'], 404),
            ('刪除存在的管理員', 'broadcaster011', 'delete', vRoom, 'broadcaster010', ['broadcaster012'], 200)
        ] 
    elif funName == 'edit':
        #scenario, account, roomId, key, value, payload, expected 
        testData = [ 
            ('僅房主可以更新該房的訊息(title)', 'broadcaster011', vRoom, 'title', 'update voice room title', {'password': '123456'}, 200),
            ('僅房主可以更新該房的訊息(description)', 'broadcaster011', vRoom, 'description', 'owner update voice room description', {'password': '123456'},200),
            ('僅房主可以更新該房的訊息(password=!@123a)', 'broadcaster011', vRoom, 'password', '!@123a', {'password': '!@123a'}, 200),
            ('僅房主可以更新該房的訊息(password=空白)', 'broadcaster011', vRoom, 'password', '', {}, 200),
            ('僅房主可以更新該房的訊息(password=None)', 'broadcaster011', vRoom, 'password', None, {}, 200), 
            ('該房的管理員可以更新(title)', 'broadcaster012', vRoom, 'title', '管理員修改聲聊房的標題123', {}, 200),
            ('該房的管理員可以更新(description)', 'broadcaster012', vRoom, 'description', '管理員修改聲聊房的描述123', {}, 200),
            ('該房的管理員可以更新(password)', 'broadcaster012', vRoom, 'password', 'qq123a', {'password': 'qq123a'}, 200),
            ('原本該房的管理員，已被移除則不可以更新(title)', 'broadcaster010', vRoom, 'title', '1房房主修改2房的標題123', {}, 403),
            ('原本該房的管理員，已被移除則不可以更新(description)', 'broadcaster010', vRoom, 'description', '1房房主修改2房的描述123', {}, 403),
            ('原本該房的管理員，已被移除則不可以更新(password)', 'broadcaster010', vRoom, 'password', 'bb123a', {'password': 'bb123a'}, 403),
            ('原本該房的管理員，已變成一般用戶則不可以更新(title)', 'broadcaster010', vRoom, 'title', '1房房主修改2房的標題123', {}, 403),
            ('原本該房的管理員，已變成一般用戶則不可以更新(description)', 'broadcaster010', vRoom, 'description', '1房房主修改2房的描述123', {}, 403),
            ('原本該房的管理員，已變成一般用戶則不可以更新(password)', 'broadcaster010', vRoom, 'password', 'bb123a', {'password': 'bb123a'}, 403),
            ('他房的房主不可以更新(title)', 'broadcaster010', vRoom, 'title', '1房房主修改2房的標題123', {}, 403),
            ('他房的房主不可以更新(description)', 'broadcaster010', vRoom, 'description', '1房房主修改2房的描述123', {}, 403),
            ('他房的房主不可以更新(password)', 'broadcaster010', vRoom, 'password', 'bb123a', {'password': 'bb123a'}, 403),
            ('經營管理者不可以更新(title)', 'tl-lisa', vRoom, 'title', '修改聲聊房的title', {}, 403),
            ('官方場控不可以更新(title)', 'lv000', vRoom, 'title', '修改聲聊房的title', {}, 403),
            ('使用者不可以更新(title)', 'track0010', vRoom, 'title', '修改聲聊房的title', {}, 403),
            ('經營管理者不可以更新(description)', 'tl-lisa', vRoom, 'description', '修改聲聊房的描述', {}, 403),
            ('官方場控不可以更新(description)', 'lv000', vRoom, 'description', '修改聲聊房的描述', {}, 403),
            ('使用者不可以更新(description)', 'track0010', vRoom, 'description', 'user cannot update description', {}, 403)
        ]
    return testData

class TestVoice():
    ws  = websocket.WebSocket()
    # def teardown_class(self):
    #     self.ws.close()

    @pytest.mark.parametrize("scenario, account, method, roomId, admin, adminList, expected", getTestData('admin'))
    def testAdminOperate(self, createInit, scenario, account, method, roomId, admin, adminList, expected):
        adList = []
        for i in adminList:
            adList.append(test_parameter[i]['id'])
        header['X-Auth-Token'] = test_parameter[account]['token']
        header['X-Auth-Nonce'] = test_parameter[account]['nonce']
        if method == 'post':
            apiName = '/api/v2/liveMaster/voiceChat/admin'
            body = {
                'roomId': roomId,
                'userId': test_parameter[admin]['id']
            }
        elif method == 'delete':
            apiName = '/api/v2/liveMaster/voiceChat/admin/' + str(roomId) + '/' + test_parameter[admin]['id']
            body = None
        res = api.apiFunction(test_parameter['prefix'], header, apiName, method, body)
        resText = json.loads(res.text)
        if expected == 200:
            voicelib.wsConnect(self.ws, test_parameter['db'], test_parameter['track0010']['token'], test_parameter['track0010']['nonce'])
            wsResult = voicelib.voiceOperator(self.ws, '1', 'vc_room:'+str(roomId), 'phx_join', {'password': '123456'})
            assert res.status_code == expected
            assert resText['Status'] == Msg[expected]['Status']
            assert resText['Message'] in Msg[expected]['Message']
            assert len(adList) == len(wsResult['payload']['data']['admins'])
            for i in adList:
                assert i in wsResult['payload']['data']['admins'], i + '不在回傳的資料中' + str(wsResult['payload']['data']['admins'])
            voicelib.voiceOperator(self.ws, '1', 'vc_room:'+str(roomId), 'phx_leave', {})
            self.ws.close()
            
    @pytest.mark.parametrize("scenario, account, roomId, key, value, payload, expected", getTestData('edit'))
    def testEditVoiceRoomInfo(self, editInit, scenario, account, roomId, key, value, payload, expected):
        body = {
            "title": "直播間標題",
            "description": "直播間簡介",
            "password": ""
        }
        if value == None:
            del body['password']
        else:
            body[key] = value 
        header['X-Auth-Token'] = test_parameter[account]['token']
        header['X-Auth-Nonce'] = test_parameter[account]['nonce']
        apiName = '/api/v2/liveMaster/voiceChat/' + str(roomId)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'patch', body)
        resText = json.loads(res.text)
        assert res.status_code == expected
        assert resText['Status'] == Msg[expected]['Status']
        assert resText['Message'] in Msg[expected]['Message']
        if expected == 200:
            time.sleep(3)
            apiName = '/api/v2/identity/voiceChat/list'
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
            resText = json.loads(res.text)
            for i in resText['data']:
                if i['id'] == roomId:
                    if key == 'password':
                        if value:
                            assert i['needPassword'] == True
                        else:
                            assert i['needPassword'] == False
                    else:
                        assert i[key] == value
                    break
            voicelib.wsConnect(self.ws, test_parameter['db'], test_parameter['track0010']['token'], test_parameter['track0010']['nonce'])
            wsResult = voicelib.voiceOperator(self.ws, '1', 'vc_room:'+str(roomId), 'phx_join', payload)
            if key == 'password':
                assert wsResult['event'] == 'voiceroom_in_bcst'
                assert len(wsResult['payload']['data']['ownerUserId']) > 0
            else:
                assert wsResult['payload']['data'][key] == value
            voicelib.voiceOperator(self.ws, '1', 'vc_room:'+str(roomId), 'phx_leave', payload)
            self.ws.close()

