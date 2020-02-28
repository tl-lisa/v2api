#/api/v2/identity/gift/list?giftCategoryId=
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
        sqlList = ["update gift set status = 0 where category_id = post_gift"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)
    
    @pytest.mark.parametrize("test_input, expected", [
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], 1], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 2], 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 3], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 2), 
        ([test_parameter['err_token'], test_parameter['err_nonce'], 1], 4)
    ])
    def testAuthAndType(self, test_input, expected):
        #驗證權限及查詢類別
        now = int(time.time()) * 1000
        apiName = '/api/v2/identity/gift/list?giftCategoryId=' + str(test_input[2]) + '&item=20&page=1'
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)    
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            if  test_input[2] < 4:
                sql = "select g.id, g.category_name, g.point, g.thumb_url, g.url, g.multiple, order_seq from gift g "
                sql += "where g.category_id in (select id from gift_category where type = '" + self.gctype[test_input[2] - 1] + "' and  status = 1 and "
                sql += "((start_time <= " + str(now) + " or start_time is null) and (end_time >= " + str(now) + " or end_time is null)) "
                sql += "and status = 1 order by g.point"
                dbResult = dbConnect.dbQuery(test_parameter['db'], sql)
                assert restext['totalCount'] == len(dbResult)
                self.totalCount = restext['totalCount'] if test_input[2] == 1 else None
                if restext['totalCount'] > 0:
                    self.giftId = restext[0]['id'] if self.giftId == '' else None
                    for i in range(restext['totalCount']):
                        assert restext[i]['id'] == dbResult[i][0]
                        assert restext[i]['categoryId'] == test_input[2]
                        assert restext[i]['name'] == dbResult[i][1]
                        assert restext[i]['point'] == dbResult[i][2]
                        assert restext[i]['thumbUrl'] == dbResult[i][3]
                        assert restext[i]['url'] == dbResult[i][4]
                        assert restext[i]['multiple'] == dbResult[i][5]
                        assert restext[i]['order_seq'] == dbResult[i][6]
            else:
                 assert restext['totalCount'] == 0

    def testStatus(self):
        #禮物以status做判斷；需加判cache 時間60秒
        sqlList = ["update gift set status = 0 where category_id = post_gift"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        time.sleep(60)
        apiName = '/api/v2/identity/gift/list?giftCategoryId=3&item=20&page=1'
        header['X-Auth-Token'] = test_parameter['backend_token']
        header['X-Auth-Nonce'] = test_parameter['backend_nonce']
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)  
        restext = json.loads(res.text)  
        assert res.status_code // 100 == 2
        assert restext['totalCount'] == 0

