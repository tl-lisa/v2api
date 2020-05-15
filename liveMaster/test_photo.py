#milestone18 加入軟刪：有comment及送禮皆軟刪
#milestone18 取得單一動態贈禮加入id(送禮記錄的id)
import time
import json
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import photo
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
cover_list = ['https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/460d7772e0ec11e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/7922266ce69111e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/118161eae8d911e9beff42010a8c0fcc',
              'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/8b640c78e8da11e9beff42010a8c0fcc']

def init():
    initdata.set_test_data(env, test_parameter)    
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idlist.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    initdata.resetData(test_parameter['db'], idlist[0])
    sqlList = ["update gift_v2 set deleted_at = NULL, is_active = 1 where uuid = '234df236-8826-4938-8340-32f39df43ed1'"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], test_parameter['photo_url'], 9)

init()

def teardown_module():
    changelist = [] 
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    changelist.append(idlist[0]) 
    api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主

def create_test_data(testName):
    testData = []
    photo_list = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idlist[0])
    pprint(photo_list)
    if testName == 'addphoto':
        testData = [
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['photo_url'], 'test123' ], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['photo_url'], '' ], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['photo_url'], '我有emoji🥰🤪#$⑤' ], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 'http://123.com.tw/123.jpg', 'test123' ], 4),
        ([test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['photo_url'], 'test123'], 4),
        ([test_parameter['err_token'], test_parameter['err_nonce'], test_parameter['photo_url'], 'test123'], 4)
        ]
    elif testName == 'addphoto2':
        testData = [
        ({}, 4), 
        ({'photoPath': test_parameter['photo_url'],  'Content': 'test123'}, 4)
        ]
    elif testName == 'delphoto':
        testData = [
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], '0'], 4),
        ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], photo_list[0]], 4),
        ([test_parameter['err_token'], test_parameter['err_nonce'], photo_list[0]], 4)
        ]
    elif testName == 'photolist':
        testData = [
            (False, [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], idlist[1], '10', '1', 0], 2),
            (True, [test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], idlist[0], '10', '1',9],2),
            (False, [test_parameter['backend_token'], test_parameter['backend_nonce'], idlist[0], '2', '1', 9],2),
            (False, [test_parameter['user_token'], test_parameter['user_nonce'], idlist[0], '2', '3', 9],2),
            (False, [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], '123abdod-alueio-123-4', '10', '1', 0], 4),
            (False, [test_parameter['err_token'], test_parameter['err_nonce'], idlist[0], '10', '1', 0], 4)
        ]
    elif testName == 'singlephoto':
        testData = [
            ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], photo_list[4]], 2),
            ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], photo_list[0]], 4),
            ([test_parameter['err_token'], test_parameter['err_nonce'], photo_list[4]], 4)
        ]
    elif testName == 'update':
        testData = [
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[0]], {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, 4),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[4]], {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, 2),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[4]], {'content': ''}, 2),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[4]], {}, 4),
            ([test_parameter['broadcaster1_token'], test_parameter['broadcaster1_nonce'], photo_list[4]], {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, 4),
            ([test_parameter['err_token'], test_parameter['err_nonce'], photo_list[4]], {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, 4)
        ]
    elif testName == 'photogift':
        testData = [
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 999], [4, 2, 'Mr.主人', 1000], False, False, True, False),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5]], [2, 2, 'Mr.主人', 1000], False, False, False, False),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5]], [2, 2, 'Mr.主人', 1000], False, False, True, True),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5]], [2, 2, 'Mr.主人', 1000], False, False, True, False),
            ([test_parameter['user_token'], test_parameter['user_nonce'], photo_list[5]], [4, 2, 'Mr.主人', 2000], False, False, True, False),
            ([test_parameter['err_token'], test_parameter['err_nonce'], photo_list[5]], [4, 2, 'Mr.主人', 2000], False, False, True, False),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5]], [2, 2, 'Mr.主人', 1000], True, False, True, False),
            ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5]], [4, 2, 'Mr.主人', 1000], False, True, True, False)      
        ]
    elif testName == 'likephoto':
        testData = [
            (False, [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], photo_list[5], 5], 2),
            (True, [test_parameter['user_token'], test_parameter['user_nonce'], photo_list[5], 5], 2),
            (False, [test_parameter['user_token'], test_parameter['user_nonce'], photo_list[0], 5], 4),
            (False, [test_parameter['err_token'], test_parameter['err_nonce'], photo_list[5], 5], 4)
        ]
    return testData


#@pytest.mark.skip()
class TestAddPhoto():
    #新增動態是以token/nonce來判斷
    @pytest.mark.parametrize("test_input, expected", create_test_data('addphoto'))
    def testAuthAndData(self, test_input, expected):
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]  
        body = {'photoPath': test_input[2],  'content': test_input[3]} 
        res = api.add_photopost(test_parameter['prefix'], header, body)
        assert res.status_code // 100 == expected
 
    @pytest.mark.parametrize("bodyValue, expected", create_test_data('addphoto2'))
    def testBodySetting(self, bodyValue, expected):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
        res = api.add_photopost(test_parameter['prefix'], header, bodyValue)    
        assert res.status_code // 100 == expected

#@pytest.mark.skip()
class TestDeletePhoto():
    # 此功能是用token/nonce來做判斷
    photo_list = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idlist[0])
    pprint(photo_list)
    delete_list = [str(photo_list[0]), str(photo_list[1]), str(photo_list[2])]
    photo.addComment(test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['prefix'], delete_list[0], '測試有註解也可正常刪除')
    photo.likePhoto(test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['prefix'], delete_list[1], 3)
    photo.sendPhotoGift(test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['prefix'], delete_list[2], '234df236-8826-4938-8340-32f39df43ed1')
    @pytest.mark.parametrize("test_input, expected", create_test_data('delphoto'))
    def testAuthAndParameter(self, test_input, expected):
        #錯誤的token/nonce
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        res = api.operator_photopost(test_parameter['prefix'], header, 'delete', test_input[2], None)
        assert res.status_code // 100 == expected
    
    def testDeleteOwnPhoto(self):
        #刪除自己且有評論的動態;有被送禮的；有被like的                   
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']     
        for i in range (len(self.delete_list)):
            res = api.operator_photopost(test_parameter['prefix'], header, 'delete', str(self.delete_list[i]), None)
            assert res.status_code == 200     
            time.sleep(7)
            res = api.get_photo_list(test_parameter['prefix'], header, idlist[0], '20', '1')
            restext = json.loads(res.text)
            assert restext['totalCount'] == 12 - (i + 1)
            res = api.operator_photopost(test_parameter['prefix'], header, 'get', str(self.delete_list[i]), '')
            assert res.status_code // 100 == 4
    
#@pytest.mark.skip()
class TestGetPhotolist():
    #此功能是任何人皆可呼叫，以livemasterid做條件 
    def teardown_module(self):
        changelist = [] 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        changelist.append(idlist[0]) 
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主
    
    @pytest.mark.parametrize("IsCreate, test_input, expected", create_test_data('photolist'))
    def testGetPhotolist(self, IsCreate, test_input, expected):
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]  
        res = api.get_photo_list(test_parameter['prefix'], header, test_input[2], test_input[3], test_input[4])
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            assert restext['totalCount'] == test_input[5]
            if test_input[5] == 0:
                assert len(restext['data']) == 0 
            else: 
                assert len(restext['data']) <=  int(test_input[3])

    def testTranstoUser(self):
        #測試直播主轉成一般user,該動態不能在被存取
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
        changelist = [] 
        changelist.append(idlist[0]) 
        api.change_roles(test_parameter['prefix'], header, changelist, '5') #轉成一般用戶
        time.sleep(30)
        res = api.get_photo_list(test_parameter['prefix'], header, idlist[0], '10', '1')
        restext = json.loads(res.text)
        assert res.status_code // 100 == 4
        assert restext['Message'] == 'User is not LiveMaster.' 
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主

    def testBlackUser(self):
        #黑名單的user不能取得動態牆的資訊
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce'] 
        body = {'userId' : idlist[2]}  
        api.add_block_user(test_parameter['prefix'], header, body)
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce'] 
        res = api.get_photo_list(test_parameter['prefix'], header, idlist[0], '10', '1')
        assert res.status_code // 100 == 4

#@pytest.mark.skip()
class TestGetSpecificalPhoto():
    @pytest.mark.parametrize("test_input, expected", create_test_data('singlephoto'))
    def testGetSpecificalPhoto(self, test_input, expected):
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        res = api.operator_photopost(test_parameter['prefix'], header, 'get', test_input[2], '')
        restext = json.loads(res.text)
        assert res.status_code // 100 == expected
        if expected == 2:
            #print(restext)
            assert restext['data']['content'] == 'test info 4'
            assert restext['data']['owner']['id'] == idlist[0]
            assert restext['data']['giftPoints'] == 0

#@pytest.mark.skip()
class TestUpdateContent():
    @pytest.mark.parametrize("test_input, body, expected", create_test_data('update'))
    def testUpdatCeontent(self, test_input, body, expected):
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        res = api.operator_photopost(test_parameter['prefix'], header, 'put', test_input[2], body)
        assert res.status_code // 100 == expected

#@pytest.mark.skip()
class TestPhotoLike():
    pid = ''
    changelist = [idlist[0]] 
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主

    @pytest.mark.parametrize("isClickagain, test_input, expected", create_test_data('likephoto'))
    def test_photoliked(self, isClickagain, test_input, expected):  
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        apiName = '/api/v2/liveMaster/photoPost/' + str(test_input[2])
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)  
        if expected == 2:                    
            restext = json.loads(res.text)
            likeNum = restext['data']['likes'] + test_input[3]
        #call like photo
        body = {'likes': test_input[3]}
        apiName1 = '/api/v2/liveMaster/photoPost/' + str(test_input[2]) + '/like'         
        res = api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)  
        assert res.status_code // 100 == expected
        if expected == 2:        
            time.sleep(30)
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)                     
            restext = json.loads(res.text)
            assert restext['data']['liked'] == True
            assert restext['data']['likes'] == likeNum 
            if isClickagain:
                api.apiFunction(test_parameter['prefix'], header, apiName1, 'post', body)  
                time.sleep(30)
                res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)                     
                restext = json.loads(res.text)
                assert restext['data']['liked'] == True
                assert restext['data']['likes'] == likeNum + test_input[3]

##@pytest.mark.skip()           
class TestGetPhotoGiftlist():
    photo_list = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idlist[0])
    giftId = '234df236-8826-4938-8340-32f39df43ed1'
    def setup_class(self):
        sqlList = []
        authList = [test_parameter['user_token'], test_parameter['user_nonce'],test_parameter['user1_token'], test_parameter['user1_nonce'],]
        sqlList.append("update remain_points set remain_points = 15000 where identity_id in( '" + idlist[2] + "', '" + idlist[3] + "')")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        for i in range(2):
            if i == 0:
                photo.sendPhotoGift(authList[i * 2], authList[i * 2 + 1], test_parameter['prefix'], self.photo_list[0], 100)
            photo.sendPhotoGift(authList[i * 2], authList[i * 2 + 1], test_parameter['prefix'], self.photo_list[5], 100)
            time.sleep(1)
    
    @pytest.fixture(scope="function")
    def initDB(self):
        print('initDB')
        sqlList = ["update gift_v2 set is_active = 1, deleted_at is NULL"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("test_input, expected, isBlack, isChangeRole, isActive, isDelete", create_test_data('photogift'))
    def testgetgiftlist(self, test_input, expected, isBlack, isChangeRole, isActive, isDelete):
        if isChangeRole:
            changelist = [idlist[0]] 
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
            api.change_roles(test_parameter['prefix'], header, changelist, '5') #轉成一般用戶
            time.sleep(30)
        if not isActive:
            sqlList = ["update gift_v2 set is_active = 0 where uuid = '" + self.giftId + "'"]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
        elif isDelete:
            sqlList = ["update gift_v2 set deleted_at = '" + (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + "' where uuid = '" + self.giftId + "'"]
            dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = '/api/v2/liveMaster/photoPost/' + str(test_input[2]) + '/giftList?item=20&page=1'
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        if isBlack:
            body = {'userId' : idlist[2]}  
            api.add_block_user(test_parameter['prefix'], header, body)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code // 100 == expected[0]
        if expected[0] == 2:
            assert restext['totalCount'] == expected[1]
            assert restext['totalPoints'] == expected[3] * restext['totalCount']
            if restext['totalCount'] > 0:
                assert restext['data'][0]['sender'] == idlist[3]
                assert restext['data'][0]['point'] == expected[3]
                assert restext['data'][0]['giftName'] == expected[2]
                assert restext['data'][0]['datetime'] >= restext['data'][1]['datetime']
                assert restext['data'][0]['id'] >= restext['data'][1]['id']

        
