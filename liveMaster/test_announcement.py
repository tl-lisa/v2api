#Milestone 16. 消息：直播主新增消息 #693,消息：取得單一消息內容 #694,消息：修改消息 #695,消息：直播主取得消息列表 #692
#Milestone 17. 消息：刪除消息 #696
import time
import json
import pytest
from ..assistence import api
from ..assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
# 過濾使用者等級，None或者空 list表示不過濾使用者等級，等級列表如下: bronze: 青銅 silver: 白銀 gold: 黃金 diamond: 鑽石 niello: 黑金
userLevel = ['niello']


def setup_module():
    initdata.set_test_data(env, test_parameter)


def teardown_module():
    pass


class TestAddMessage():  # 消息：直播主新增消息 #693
    def test_HappyPath(self):
        # 直播主發送每月一次的訊息
        global ID
        apiName = '/api/v2/liveMaster/announcement/'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '直播主測試title',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert restext['Status'] == 'Ok'
        ID = restext['data']['id']
        assert int(res.status_code / 100) == 2

    def test_TwiceAMonth(self):
        # 直播主重複發送訊息測試，單月不可超過一次
        apiName = '/api/v2/liveMaster/announcement/'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '直播主測試title',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 406

    def test_TitleOver20(self):
        # 直播主發送訊息標題超過20
        apiName = '/api/v2/liveMaster/announcement/'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '123456789012345678901',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 406

    def test_ContentOver500(self):
        # 直播主發送訊息內容超過500
        apiName = '/api/v2/liveMaster/announcement/'
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': 'tittle',
                'content': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 406

    def test_ErrAuth(self):
        # Auth 檢驗沒過關
        apiName = '/api/v2/liveMaster/announcement/'
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '直播主測試title',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 401


class TestGetSingleAnnounce():  # 消息：取得單一消息內容 #694
    def test_HappyPath(self):
        # Get單一特定訊息，確認各欄位資訊正確
        #global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        pprint(ID)
        apiName = apiName.replace('{announcement id}', str(ID))
        pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert restext['data']['id'] == ID
        assert restext['data']['title'] == '直播主測試title'
        assert restext['data']['content'] == '直播主測試content，內容123,abc~'
        assert restext['data']['userLevel'] == userLevel
        assert int(res.status_code / 100) == 2

    def test_ErrAuth(self):
        # Auth 檢驗沒過關 401
        #global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        pprint(ID)
        apiName = apiName.replace('{announcement id}', str(ID))
        pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 401

    def test_ErrID(self):
        # Auth ID錯誤 40X
        #global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        FakeID = ID+1111
        print('FakeID = ', FakeID)
        apiName = apiName.replace('{announcement id}', str(FakeID))
        pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        # 暫定4開頭，等規格定下在決定
        assert int(res.status_code / 100) == 4


def GetData(title, content, UserLevel, siwtch):
    apiName = '/api/v2/liveMaster/announcement/{announcement id}'
    pprint(ID)
    apiName = apiName.replace('{announcement id}', str(ID))
    pprint('apiName = ' + apiName)
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    header['Content-Type'] = 'application/json'
    res = api.apiFunction(
        test_parameter['prefix'], header, apiName, 'get', None)
    restext = json.loads(res.text)
    pprint(restext)
    if siwtch == True:
        assert restext['data']['id'] == ID
        assert restext['data']['title'] == title
        print('GetData title = '+title)
        assert restext['data']['content'] == content
        print('GetData content = '+content)
        assert restext['data']['userLevel'] == UserLevel
        print('GetData userLevel = '+UserLevel)
        assert int(res.status_code / 100) == 2
    else:
        #assert restext['data']['id'] == ID
        assert restext['data']['title'] != title
        print('GetData title = '+title)
        assert restext['data']['content'] != content
        print('GetData content = '+content)
        # assert restext['data']['userLevel'] == UserLevel
        # print('GetData userLevel = '+UserLevel)
        assert int(res.status_code / 100) == 2


class TestEditMessage():  # 消息：修改消息 #695
    def test_HappyPath(self):
        # 修改訊息
        # 過濾使用者等級，None或者空 list表示不過濾使用者等級，等級列表如下: bronze: 青銅 silver: 白銀 gold: 黃金 diamond: 鑽石 niello: 黑金
        title = '測試直播主消息修改title'
        content = '我應該修改成功了吧？'
        siwtch = False
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        apiName = apiName.replace('{announcement id}', str(ID))
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': title,
                'content': content, 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code / 100) == 2
        GetData(title, content, userLevel, siwtch)

    def test_EditTittleOver20(self):
        # tittle超過長度
        title = '123456789012345678901'
        content = 'tittle超過長度'
        siwtch = False
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
       # pprint(ID)
        apiName = apiName.replace('{announcement id}', str(ID))
      #  pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': title,
                'content': content, 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 406
        GetData(title, content, userLevel, siwtch)

    def test_EditContentOver500(self):
        # 內容超過長度
        title = '內容超過長度'
        content = '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901'
        siwtch = False
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
       # pprint(ID)
        apiName = apiName.replace('{announcement id}', str(ID))
       # pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': title,
                'content': content, 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 406
        GetData(title, content, userLevel, siwtch)

    def test_FakeID(self):
        # 訊息不存在
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        FakeID = ID+1111
        print('FakeID = ', FakeID)
        apiName = apiName.replace('{announcement id}', str(FakeID))
       # pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '測試直播主消息修改title',
                'content': '我應該修改成功了吧？', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        assert res.status_code == 404

    def test_ErrAuth(self):
        # Auth 檢驗沒過關
        #global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        apiName = apiName.replace('{announcement id}', str(ID))
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '直播主測試title',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)

        assert int(res.status_code) == 401

    def test_NotMasterID(self):
        # 送出之後應檢查欲修改的消息 id是否為該直播主發佈的，否則擋住。
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        apiName = apiName.replace('{announcement id}', str(ID))
        header['X-Auth-Token'] = test_parameter['broadcaster1_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster1_nonce']
        header['Content-Type'] = 'application/json'
        body = {'title': '直播主測試title',
                'content': '直播主測試content，內容123,abc~', 'userLevel': userLevel}
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'post', body)
        restext = json.loads(res.text)
        pprint(restext)
        print('status_code = ', res.status_code)
        assert int(res.status_code) // 100 == 4


class TestGetList():  # 消息：直播主取得消息列表 #692
    def test_HappyPath(self):
        #global totalCount
        apiName = '/api/v2/liveMaster/announcement/list'
        #pprint('apiName = ' + apiName)
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert restext['Status'] == 'Ok'
        assert int(res.status_code / 100) == 2


def Getrestext():
    apiName = '/api/v2/liveMaster/announcement/list'
    #pprint('apiName = ' + apiName)
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    header['Content-Type'] = 'application/json'
    res = api.apiFunction(
        test_parameter['prefix'], header, apiName, 'get', None)
    restext = json.loads(res.text)
    #restextList = restext
    assert restext['Status'] == 'Ok'
    totalCount = str(restext['totalCount'])
    print('total = '+totalCount)
    assert int(res.status_code / 100) == 2
    return restext


# @pytest.mark.skip('skip')
class TestDelMes():  # 消息：刪除消息 #696
    def test_HappyPath(self):
        # 刪除一整頁的消息
        restextList = Getrestext()
        totalCount = restextList['totalCount']
        FirstTotalCount = totalCount
        print('totalCount = ', totalCount)
        if totalCount >= 20:
            idlist = ['' for i in range(19)]
            totalCount = 19
            print('totalCount = ', totalCount)
        else:
            idlist = ['' for i in range(totalCount)]

        for i in range(totalCount):
            print('i = ', i)
            idlist[i] = str(restextList['data'][i]['id'])
            apiName = '/api/v2//liveMaster/announcement/{announcement id}'
            apiName = apiName.replace('{announcement id}', str(idlist[i]))
            print('apiName = ', apiName)
            header['X-Auth-Token'] = test_parameter['broadcaster_token']
            header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
            header['Content-Type'] = 'application/json'
            res = api.apiFunction(
                test_parameter['prefix'], header, apiName, 'delete', None)
            restext = json.loads(res.text)
            assert restext['Status'] == 'Ok'
            assert int(res.status_code / 100) == 2
        # 用total數量驗證是否正確
        time.sleep(6)
        restext = json.loads(res.text)
        pprint(restext)
        restextList = Getrestext()
        AfterTotalCount = restextList['totalCount']
        assert int(AfterTotalCount) == int((FirstTotalCount - totalCount))
       # print('idlist範圍 = ', idlist)

    def test_ErrAuth(self):
        # Auth 檢驗沒過關
        global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        apiName = apiName.replace('{announcement id}', str(ID))
        header['X-Auth-Token'] = test_parameter['err_token']
        header['X-Auth-Nonce'] = test_parameter['err_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'delete', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 401

    def test_NoMessage(self):
        # 404	消息不存在
        global ID
        apiName = '/api/v2/liveMaster/announcement/{announcement id}'
        apiName = apiName.replace('{announcement id}', str(ID+1000))
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        header['Content-Type'] = 'application/json'
        res = api.apiFunction(
            test_parameter['prefix'], header, apiName, 'delete', None)
        restext = json.loads(res.text)
        pprint(restext)
        assert int(res.status_code) == 404
