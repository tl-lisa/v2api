#milestone18 加入軟刪：有comment及送禮皆軟刪
#milestone18 取得單一動態贈禮加入id(送禮記錄的id)
#milestone25 加入vedio影音功能 #1462，1463，1464
import time
import json
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import photo
from pprint import pprint
from datetime import datetime, timedelta

Msg = {
    200:{'Status': 'Ok', 'Message': 'SUCCESS'},
    401:{'Status': 'Error', 'Message': '使用者驗證錯誤，請重新登入'},
    403:{'Status': 'Error', 'Message': ['PERMISSION_REQUIRED', '抱歉，您的使用權限不足！如有疑問，請洽初樂客服人員。', '該貼文無法檢視']},
    400:{'Status': 'Error', 'Message': ['PARAM_TYPE_ERROR', 'OWNER_IS_NOT_LIVEMASTER', 'LACK_OF_NECESSARY_PARAMS','USER_HAS_BEEN_BLOCKED']},
    404:{'Status': 'Error', 'Message': ['GIFT_CATAGORY_NOT_FOUND', 'MEDIA_NOT_FOUND', 'LIVEMASTER_NOT_FOUND', '不存在的動態貼文']}
}
env = 'QA'
test_parameter = {}
cards = []
idlist = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
#urlList[photo_url, preview_url, video_url, wrong_url]
urlList = [
    'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png',
    'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/096ee460b45c11eab2d142010a8c0017.png',
    'https://d3eq1e23ftm9f0.cloudfront.net/story/vedio/ef79cfbab45c11eab2d142010a8c0017.mp4',
    'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103x048cd11ea83b942010a8c0017.jpg',
]

def setup_module():
    initdata.set_test_data(env, test_parameter)    
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'] , 
    [test_parameter['broadcaster_acc'], test_parameter['broadcaster1_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idlist)
    sqlList = ["update gift_v2 set deleted_at = NULL, is_active = 1 where uuid = '234df236-8826-4938-8340-32f39df43ed1'"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)

def teardown_module():
    changelist = [idlist[0]] 
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主

 
def getTestData(testName): 
    testData = []
    if testName == 'addPhoto': 
        #scenario, token, nonce, body, expected
        testData = [
            ('直播主上傳動態_照片', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('photo', urlList[0], '動態照片上傳', '', '', '108'), 200),
            ('直播主上傳動態未給type,應預設', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('', urlList[0], '動態照片上傳', '', '', '108'), 200),
            ('直播主上傳動態_影音檔', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('video', '', '動態影片上傳', urlList[1], urlList[2], '108'), 200),
            ('直播主上傳動態_影音檔但未設禮物類別', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('video', '', '動態影片上傳', urlList[1], urlList[2], ''), 400),
            ('直播主上傳動態_照片，但url不存在', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('photo', urlList[3], '動態照片上傳', '', '', '108'), 404),
            ('直播主上傳動態_影音檔，但url不存在', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('video', '', '動態影片上傳', urlList[3], urlList[2], '108'), 404),
            ('直播主上傳動態_影音檔，但預覧url空值', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('video', '', '動態影片上傳', urlList[1], '', '108'), 404),
            ('直播主上傳動態_照片，但禮物類別不存在', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('photo', urlList[0], '動態照片上傳', '', '', '399'), 404),
            ('直播主上傳動態_照片，但未設禮物類別', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('photo', urlList[0], '動態照片上傳', '', '', ''), 200),
            ('直播主上傳動態_未設type且未設禮物類別', 'broadcaster_token', 'broadcaster_nonce', photo.createBody('', urlList[0], '動態照片上傳', '', '', ''), 200),
            ('token_nonce不存在', 'err_token', 'err_nonce', photo.createBody('photo', urlList[0], '動態照片上傳', '', '', '108'), 401),
            ('使用者上傳照片', 'user_token', 'user_nonce', photo.createBody('photo', urlList[0], '動態照片上傳', '', '', '108'), 403)
        ]
    elif testName == 'photolist':
        #scenario, token, nonce, masterId, items, pages, totalCount, expected
        testData = [
            ('取得該直播主動態列表_有資料', 'backend_token', 'backend_nonce', 0, 10, 1, 3, '', 200),
            ('取得該直播主動態列表_無資料', 'broadcaster_token', 'broadcaster_nonce', 1, 10, 1, 0, '', 200),
            ('取得該直播主動態列表_指定item＝1;page=1', 'user_token', 'user_nonce', 0, 1, 1, 3, '', 200),
            ('user被列入黑名單，無法取得該直播主的動態列表', 'user1_token', 'user1_nonce', 0, 10, 1, 0, 'block', 400),
            ('原直播主轉成一般user，其動態無法再取得', 'user_token', 'user_nonce', 0, 10, 1, 0, 'changeRole', 400),
            ('auth 不存在', 'err_token', 'err_nonce', 0, 10, 1, 3, '', 401) 
        ]
    elif testName == 'singlePhoto':
             #scenario, token, nonce, postId, action, isLike, likeNum, totalLike, comment, totalComment, expected (photo like合併驗證)
        testData = [
            ('指定動態id', 'backend_token', 'backend_nonce', 1, '', False, 0, 0, '', 0, 2),
            ('指定動態id不存在', 'backend_token', 'backend_nonce', 0, '', False, 0, 0, '', 0, 4),
            ('對指定的動態id按喜歡', 'user_token', 'user_nonce', 1, 'like', True, 10, 10, '', 0, 2),
            ('指定有被按喜歡動態id', 'user1_token', 'user1_nonce', 1, '', False, 0, 10, '', 0, 2),
            ('指定有被加過評論的動態id', 'user1_token', 'user1_nonce', 1, 'comment', False, 0, 10, 'like 直播主😎🥳㊙️^-^！① ', 1, 2),
            ('指定已被刪除的動態id', 'user1_token', 'user1_nonce', 2, 'delete', False, 0, 10, '', 0, 4),
            ('原直播主轉成一般user，其動態無法再取得', 'user_token', 'user_nonce',  1, 'changeRole', False, 0, 10, '', 0, 4),
            ('user被列入黑名單，無法取得該直播主的動態', 'user1_token', 'user1_nonce', 1, 'block', False, 0, 10, '', 0, 4),
            ('auth 不存在', 'err_token', 'err_nonce', 1, '', False, 0, 10, '', 0, 4)
        ]
    elif testName == 'updatePhoto':
            #scenario, token, nonce, body, origenal, action, expected
        testData = [
            ('直播主修改個人動態說明_動態說明含emoji', 'broadcaster_token', 'broadcaster_nonce', {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, '動態照片上傳', '', 200),
            ('直播主修改個人動態說明_動態說明為空字串', 'broadcaster_token', 'broadcaster_nonce', {'content': ''}, 'wahaha 😎🥳㊙️^-^！①  %。。。', '', 200),
            ('直播主修改個人動態說明_body不正確', 'broadcaster_token', 'broadcaster_nonce', {}, '', '', 400),
            ('直播主修改不屬於自己的動態說明', 'broadcaster1_token', 'broadcaster1_nonce', {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, '', '', 401),
            ('直播主轉為非直播主，修改自己的動態說明', 'broadcaster_token', 'broadcaster_nonce', {'content': 'wahaha 😎🥳㊙️^-^！①  %。。。'}, '', 'changeRole', 401)
        ]
    elif testName == 'deletePhoto':
            #scenario, token, nonce, postId, action, totalCount, expected
        testData = [
            ('直播主不可刪除非自己的動態 ', 'broadcaster1_token', 'broadcaster1_nonce', 1, '', 3, 400),
            ('直播主可刪除有加評論的動態', 'broadcaster_token', 'broadcaster_nonce',  1, 'comment', 2, 200),
            ('直播主可刪除有被按喜歡的動態', 'broadcaster_token', 'broadcaster_nonce', 2, 'like', 1, 200),
            ('直播主可刪除有被送禮物的動態', 'broadcaster_token', 'broadcaster_nonce', 3, 'sendGift', 0, 200)
        ]
    elif testName == 'photoGift':
            #scenario, token, nonce, action, totalCount, expected      
        testData = [
            ('直播主無法查到非自己動態送禮明細', 'broadcaster1_token', 'broadcaster1_nonce', '', '', 400), 
            ('禮物下架仍可在送禮記錄裡查到', 'broadcaster_token', 'broadcaster_nonce',  1, 'inactive', 1, 200),
            ('禮物已被刪除仍可在送禮記錄裡查到', 'broadcaster_token', 'broadcaster_nonce', 2, 'deleted', 1, 200),
            ('送禮者雖被列入黑名單，仍可在送禮記錄裡查到', 'broadcaster_token', 'broadcaster_nonce', 3, 'block', 1, 200),
            ('直播主轉成一般使用者則無法查詢送禮記錄', 'broadcaster_token', 'broadcaster_nonce', 3, 'changeRole', 1, 400)
        ]
    return testData


class TestPhotoOfMaster():
    #新增動態是以token/nonce來判斷
    @pytest.mark.parametrize("scenario, token, nonce, body, expected", getTestData('addPhoto'))
    def testAdd(self, scenario, token, nonce, body, expected):
        res = photo.createPhoto(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], body)
        restext = json.loads(res.text)
        assert res.status_code  == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        
    @pytest.mark.parametrize("scenario, token, nonce, body, origenal, action, expected", getTestData('updatePhoto'))
    def testUpdate(self, scenario, token, nonce, body, origenal, action, expected):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter[token], test_parameter[nonce], idlist[3]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idlist[0]], 5]}
        }
        if action != '':
            actionDic[action]['funName'](*actionDic[action]['parameter'])
        res = photo.updatePhoto(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], 1, body)
        restext = json.loads(res.text)
        assert res.status_code  == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if action == '':
            res = photo.SpecificalPhoto(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], 1)   
            restext = json.loads(res.text)
            if expected == 200:
                assert restext['data']['content'] == body['content']  
            else:
                assert restext['data']['content'] == origenal
        

class TestPhotoOperate():
    createPhotoList = [
        ['photo', urlList[0], '動態照片上傳1', '', '', '108'],
        ['video', '', '動態影片上傳1', urlList[1], urlList[2], '108'],
        ['', urlList[0], '動態照片上傳2', '', '', '']
    ]
   
    #此功能是任何人皆可呼叫，以livemasterid做條件，或指定postid
    def setup_class(self):
        initdata.clearPhoto(test_parameter['db'])
        for i in self.createPhotoList:
            body = photo.createBody(*i)
            photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], body)

    def setup_method(self):
        changelist = [idlist[0]] 
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
        api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主
 
    @pytest.mark.parametrize("scenario, token, nonce, masterId, items, pages, totalCount, action, expected", getTestData('photolist'))
    def testGetPhotolist(self, scenario, token, nonce, masterId, items, pages, totalCount, action, expected):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], idlist[3]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idlist[0]], 5]}
        }
        actionDic[action]['funName'](*actionDic[action]['parameter']) if action != '' else None
        time.sleep(30)
        res = photo.getPhotoList(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], idlist[masterId], items, pages)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            assert restext['totalCount'] == totalCount
            if totalCount > 0:
                if items > 1:
                    assert restext['data'][0]['id'] > restext['data'][1]['id']
                assert len(restext['data']) <=  items
                for i in range(len(restext['data'])):
                    assert restext['data'][i]['content'] == self.createPhotoList[abs(i-2)][2]
                    assert restext['data'][i]['owner']['id'] == idlist[0]
                    assert len(restext['data'][i]['owner']['profilePicture']) > 0
                    if restext['data'][i]['type'] == 'photo':
                        assert restext['data'][i]['photoPath'] == self.createPhotoList[abs(i-2)][1]
                        if self.createPhotoList[abs(i-2)][5] != '':
                            assert restext['data'][i]['giftCategoryId'] == int(self.createPhotoList[abs(i-2)][5])
                        else:
                            assert restext['data'][i]['giftCategoryId'] == None
                    else:
                        assert restext['data'][i]['photoPath'] ==  restext['data'][i]['previewPath']
                        assert restext['data'][i]['videoPath'] == self.createPhotoList[abs(i-2)][4]
                        assert restext['data'][i]['previewPath'] == self.createPhotoList[abs(i-2)][3]
                        assert restext['data'][i]['giftCategoryId'] == int(self.createPhotoList[abs(i-2)][5])

    @pytest.mark.parametrize("scenario, token, nonce, postId, action, isLike, likeNum, totalLike, comment, totalComment, expected", getTestData('singlePhoto'))
    def testGetSpecificalPhoto(self, scenario, token, nonce, postId, action, isLike, likeNum, totalLike,comment, totalComment, expected):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], idlist[3]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idlist[0]], 5]},
            'like':{'funName': photo.likePhoto, 'parameter': [test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId, likeNum]},
            'delete':{'funName': photo.delPhoto, 'parameter': [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], postId]},
            'comment':{'funName': photo.addComment, 'parameter': [test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId, comment]}
        }
        actionDic[action]['funName'](*actionDic[action]['parameter']) if actionDic.get(action) else None
        time.sleep(30)
        res = photo.SpecificalPhoto(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId)        
        restext = json.loads(res.text)
        assert res.status_code // 100  == expected
        assert restext['Status'] == Msg[res.status_code]['Status']
        assert restext['Message'] in Msg[res.status_code]['Message']
        if expected == 2:
            assert restext['data']['content'] == self.createPhotoList[postId - 1][2]
            assert restext['data']['comments'] == totalComment
            assert restext['data']['owner']['id'] == idlist[0]
            assert len(restext['data']['owner']['profilePicture']) > 0
            assert restext['data']['liked'] == isLike
            assert restext['data']['likes'] == totalLike
            if restext['data']['type'] == 'photo':
                assert restext['data']['photoPath'] == self.createPhotoList[postId - 1][1]
                assert restext['data']['giftCategoryId'] == int(self.createPhotoList[postId - 1][5])
            else:
                assert restext['data']['videoPath'] == self.createPhotoList[postId - 1][3]
                assert restext['data']['previewPath'] == self.createPhotoList[postId - 1][4]
                assert restext['data']['giftCategoryId'] == int(self.createPhotoList[postId - 1][5])

class TestDelPhoto():
    createPhotoList = [
        ['photo', urlList[0], '動態照片上傳', '', '', '108'],
        ['video', '', '動態影片上傳', urlList[1], urlList[2], '108'],
        ['photo', urlList[0], '動態照片上傳', '', '', '']
    ]
    photoIdList = [99]

    #此功能是任何人皆可呼叫，以livemasterid做條件，或指定postid
    def setup_class(self):
        initdata.clearPhoto(test_parameter['db'])
        for i in range(3):
            body = photo.createBody(self.createPhotoList[i][0], self.createPhotoList[i][1], self.createPhotoList[i][2], self.createPhotoList[i][3], self.createPhotoList[i][4], self.createPhotoList[i][5])
            photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], body)
        res = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], idlist[0], 10, 1)
        restext = json.loads(res.text)
        for i in restext['data']:
            self.photoIdList.append(i['id'])
    
    @pytest.mark.parametrize("scenario, token, nonce, postId, action, totalCount, expected", getTestData('singlePhoto'))
    def testDeletePhoto(self, scenario, token, nonce, postId, action, totalCount, expected):
        actionDic = {
            'like':{'funName': photo.likePhoto, 'parameter': [test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId, 10]},
            'sendGift':{'funName': photo.sendPhotoGift, 'parameter': [test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], postId, '234df236-8826-4938-8340-32f39df43ed1']},
            'comment':{'funName': photo.addComment, 'parameter': [test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId, '測試有註解也可正常刪除']}
        }
        if action != '':
            actionDic[action]['funName'](*actionDic[action]['parameter'])
        time.sleep(30)
        res = photo.delPhoto(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], postId)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        res = photo.getPhotoList(test_parameter[token], test_parameter[nonce], test_parameter['prefix'], idlist[0], '10', '1')
        restext = json.loads(res.text)
        restext['totalCount'] == totalCount

class TestGetPhotoSendGiftList():
    giftId = '234df236-8826-4938-8340-32f39df43ed1'
    giftPoint = 1000
    giftName = 'Mr.主人'
    createPhotoList = ['photo', urlList[0], '動態照片上傳', '', '', '108']   
    photoIdList = [99]
    def setup_class(self):
        initdata.clearPhoto(test_parameter['db'])
        dbConnect.dbSetting(test_parameter['db'], ["update remain_points set remain_points = 15000 where identity_id in( '" + idlist[2] + "', '" + idlist[3] + "')", 
        "update gift_v2 set is_active = 1, deleted_at is NULL"])
        photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], photo.createBody(*self.createPhotoList))
        for i in range(2):
            photo.sendPhotoGift(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], test_parameter['prefix'], 1, self.giftId)
        time.sleep(1)
    
    @pytest.mark.parametrize("scenario, token, nonce, action, totalCount, expected", getTestData('photoGift'))
    def testGetGiftList(self, scenario, token, nonce, action, totalCount, expected):
        actionDic = {
            'block': {'funName': api.blockUser, 'parameter': [test_parameter['prefix'], test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], idlist[3]]},
            'changeRole': {'funName': api.changeRole, 'parameter': [test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [idlist[0]], 5]},
            'inactive': "update gift_v2 set is_active = 0 where uuid = '" + self.giftId + "'",
            'deleted': "update gift_v2 set deleted_at = '" + (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + "' where uuid = '" + self.giftId + "'"
        }
        if action in ('block', 'changeRole'):
            actionDic[action]['funName'](*actionDic[action]['parameter'])
        elif action in ['inactive', 'deleted']:
            dbConnect.dbSetting(test_parameter['db'], [actionDic[action]])
        time.sleep(30)
        apiName = '/api/v2/liveMaster/photoPost/1/giftList?item=20&page=1'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == expected
        if expected == 200:
            assert restext['totalCount'] == totalCount
            assert restext['totalPoints'] == self.giftPoint * totalCount
            if restext['totalCount'] > 0:
                assert restext['data'][0]['sender'] == idlist[2]
                assert restext['data'][0]['point'] == self.giftPoint
                assert restext['data'][0]['giftName'] == self.giftName
                assert restext['data'][0]['datetime'] >= restext['data'][1]['datetime']
                assert restext['data'][0]['id'] >= restext['data'][1]['id']
