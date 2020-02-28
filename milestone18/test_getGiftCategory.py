#/api/v2/identity/giftCategory/list?type=
#mileston 18 加入軟刪及判斷delete_at
import json
import requests
import pymysql
import time
import string
import pytest
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}


initdata.set_test_data(env, test_parameter)


class TestGetGiftCategory():
    gctype = ['live_room', 'liveshow', 'post_gift', 'instant_message']
    
    def setup_class(self):
        sqlList = ["update gift_category set end_time = NULL, start_time = NULL where status = 1"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)
    
    @pytest.mark.parametrize("test_input, expected", [
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], 1], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 2], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 3], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 5], 5),
        ([test_parameter['err_token'], test_parameter['err_nonce'], 1], 4)
    ])
    def testAuthAndType(self, test_input, expected):
        #驗證權限及查詢類別
        now = int(time.time()) * 1000
        apiName = '/api/v2/identity/giftCategory/list?type=' + str(test_input[2]) + '&item=20&page=1'
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)  
        restext = json.loads(res.text)
        pprint(restext)  
        assert res.status_code // 100 == expected
        if expected == 2:
            if  test_input[2] < 5:
                sql = "select id, category_name, banner, url from gift_category where type = '" + self.gctype[test_input[2] - 1] + "' and  status = 1 and "
                sql += "((start_time <= " + str(now) + " or start_time is null) and (end_time >= " + str(now) + " or end_time is null))order by id desc"
                dbResult = dbConnect.dbQuery(test_parameter['db'], sql)
                #pprint(dbResult)
                assert restext['totalCount'] == len(dbResult)
                if restext['totalCount'] > 0:
                    for i in range(restext['totalCount']):
                        assert restext['data'][i]['id'] == dbResult[i][0]
                        assert restext['data'][i]['type'] == test_input[2]
                        assert restext['data'][i]['categoryName'] == dbResult[i][1]
                        assert restext['data'][i]['banner'] in ('', dbResult[i][2])
                        assert restext['data'][i]['url'] in ('', dbResult[i][2])
            else:
                assert restext['totalCount'] == 0

    @pytest.mark.parametrize("start_time, end_time, expected", [
        (str(int(time.time() + 180) * 1000), str(int(time.time() + 300) * 1000), 0),
        (str(int(time.time() + 61) * 1000), str(int(time.time() + 180) * 1000), 1),
        (str(int(time.time() - 180) * 1000), str(int(time.time() - 120) * 1000), 0),
        (str(int(time.time() - 180) * 1000), str(int(time.time() + 62) * 1000), 1)
        ])
    def testExpiryTime(self, start_time, end_time, expected):
        #禮物類別的start time大於目前時間，不應查出；需加判cache 時間60秒
        time.sleep(60)
        sqlList = ["update gift_category set end_time = " + end_time + ", start_time = " + start_time + " where type = 'post_gift'"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        apiName = '/api/v2/identity/giftCategory/list?type=3&item=20&page=1'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)  
        restext = json.loads(res.text)  
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == expected

