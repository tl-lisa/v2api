import time
import json
from ..assistence import api
from ..assistence import initdata
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
cards = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

def setup_module():
    initdata.set_test_data(env, test_parameter)    

def teardown_module():
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    mid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header) 
    #reset onairtime
    res = api.get_onairtime(test_parameter['prefix'], mid, header)
    json_result = json.loads(res.text)
    for i in json_result['data']:
        api.del_onairtime(test_parameter['prefix'], header, i['type'], i['id'])


class TestliveOnairtime():
    def test_set_onetime(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # onAitTime空值
        body = {'type': 'oneTime', 'onAirTime': ''}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        json_result = json.loads(res.text)
        assert json_result['Status'] == 'Error'    

        # onAirTime格式不對
        body = {'type': 'oneTime', 'onAirTime': '00:00', 'timeZone': '+0800'}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        json_result = json.loads(res.text)
        assert json_result['Status'] == 'Error'

        # onAirTime type不對
        body = {'type': 'repeat', 'repeat': test_parameter['one_time_1'], 'timeZone': '+0800'}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        json_result = json.loads(res.text)
        assert res.status_code == 406
        assert json_result['Status'] == 'Error'

        # one time開播時間最多設定3筆，第4筆會發生錯誤
        for i in range(5):
            body = {'type': 'oneTime', 'onAirTime': test_parameter['one_time_1'] + i * 300}
            res = api.set_onairtime(test_parameter['prefix'], body, header)
            json_result = json.loads(res.text)
            if i < 4:
                assert res.status_code == 200
                if i > 0:
                    assert json_result['data'][0]['onAirTime'] >= int(time.time())
            else:
                assert res.status_code == 406


    def test_set_repeat_time(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # 輸入錯誤的type
        body = {'type': 'onetime', 'repeatTime': {'week': [1, 3, 5], 'onAirTime': '18:00:00', 'timeZone': '+0800'}}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        assert res.status_code == 406

        # 輸入錯誤的onAirTime
        body = {'type': 'repeat', 'repeatTime': {'week': [1, 3, 5], 'onAirTime': 1578932584, 'timeZone': '+0800'}}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        assert res.status_code == 406

        # 輸入錯誤的onAirTime格式
        body = {'type': 'repeat', 'repeatTime': {'week': [1, 3, 5], 'onAirTime': '24:00:00', 'timeZone': '+0800'}}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        assert res.status_code == 406

        # repeat最多僅能1筆，加入第2筆就會有錯
        body = {'type': 'repeat', 'repeatTime': {'week': [1, 3, 5], 'onAirTime': '18:00:00', 'timeZone': '+0800'}}
        for i in range(2):
            res = api.set_onairtime(test_parameter['prefix'], body, header)
            json_result = json.loads(res.text)
            if i < 1:
                assert res.status_code == 200
            else:
                assert json_result['Message'] == 'Invaild AirTimeRepeat settings.'
                assert json_result['Status'] == 'Error'


    def test_get_onairtime(self):
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        # uid不存在
        uid = '1234EERR'
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        assert res.status_code == 404

        # uid為粉絲
        uid = api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        assert json_result['Message'] == 'User is not LiveMaster.'
        assert json_result['Status'] == 'Error'
    
        # uid為直播主
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        assert res.status_code == 200
        assert len(json_result['data']) > 0

        # uid為直播主但未設定過開播時間
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster2_acc'], header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        assert res.status_code == 200
        assert len(json_result['data']) == 0


    def test_delete_onairtime(self):
        header1 = {'Content-Type': 'application/json', 'Connection': 'Keep-alive',
                'X-Auth-Token': test_parameter['broadcaster1_token'],
                'X-Auth-Nonce': test_parameter['broadcaster1_nonce']}
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        for i in json_result['data']:
            # 刪非自己的直播時間
            res = api.del_onairtime(test_parameter['prefix'], header1, i['type'], i['id'])
            assert res.status_code == 404

            # type正確但ID不存在
            res = api.del_onairtime(test_parameter['prefix'], header, i['type'], i['id'] - 30)
            assert res.status_code == 404
            if i['type'] == 'oneTime':
                errtype = 'repeat'
            else:
                errtype = 'oneTime'

            # ID存在但type不正確
            res = api.del_onairtime(test_parameter['prefix'], header, errtype, i['id'])
            assert res.status_code == 404

            # ID存在但type不存在
            res = api.del_onairtime(test_parameter['prefix'], header, 'fake', i['id'])
            json_result = json.loads(res.text)
            assert json_result['Message'] == 'Invaild AirTime settings.'
            assert json_result['Status'] == 'Error'

            # 刪除正確的資料
            res = api.del_onairtime(test_parameter['prefix'], header, i['type'], i['id'])
            assert res.status_code == 200


    def test_repeat_timeZone(self):  
        iscrossweek = True  
        header['X-Auth-Token'] = test_parameter['broadcaster_token']
        header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
        uid = api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header)
        body = {'type': 'repeat', 'repeatTime': {'week': [1, 3, 5], 'onAirTime': '18:00:00', 'timeZone': '+0800'}}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        for i in json_result['data'][0]['repeatTime']['week']:
            if i == datetime.date.today().isoweekday():
                format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
                format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
                onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))))
                if int(onairtime) >= int(time.time()):
                    iscrossweek = False
                    break  
            elif i > datetime.date.today().isoweekday():
                interval_date = i - datetime.date.today().isoweekday()
                format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day + interval_date)
                format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
                onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))))
                iscrossweek = False
                break  
        if iscrossweek:
            interval_date = 7 - datetime.date.today().isoweekday() + json_result['data'][0]['repeatTime']['week'][0]
            format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day + interval_date)
            format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
            onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))))
        res = api.namecard_operator(test_parameter['prefix'], header, 'get', uid,'')
        result1 = json.loads(res.text)  
        assert result1['data']['onAirTime'] == int(onairtime)
        res = api.del_onairtime(test_parameter['prefix'], header, json_result['data'][0]['type'], json_result['data'][0]['id'])       
        
        body = {'type': 'repeat', 'repeatTime': {'week': [2, 4, 6], 'onAirTime': '18:00:00', 'timeZone': '+0900'}}
        res = api.set_onairtime(test_parameter['prefix'], body, header)
        res = api.get_onairtime(test_parameter['prefix'], uid, header)
        json_result = json.loads(res.text)
        for i in json_result['data'][0]['repeatTime']['week']:
            if i == datetime.date.today().isoweekday():
                format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day)
                format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
                onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))) - 3600)
                if int(onairtime) >= int(time.time()):
                    iscrossweek = False
                    break  
            elif i > datetime.date.today().isoweekday():
                interval_date = i - datetime.date.today().isoweekday()
                format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day + interval_date)
                format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
                onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))) - 3600)
                iscrossweek = False
                break  
        if iscrossweek:
            interval_date = 7 - datetime.date.today().isoweekday() + json_result['data'][0]['repeatTime']['week'][0]
            format_time = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(datetime.date.today().day + interval_date)
            format_time = format_time + ' ' + json_result['data'][0]['repeatTime']['onAirTime']
            onairtime = str(int(time.mktime(time.strptime(format_time, "%Y-%m-%d %H:%M:%S"))) - 3600)
        res = api.namecard_operator(test_parameter['prefix'], header, 'get', uid,'')
        result1 = json.loads(res.text)   
        assert result1['data']['onAirTime'] == int(onairtime)
        res = api.del_onairtime(test_parameter['prefix'], header, json_result['data'][0]['type'], json_result['data'][0]['id'])       
