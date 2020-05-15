#/api/v2/identity/gift/list?giftCategoryId=
#mileston 18 加入軟刪及判斷delete_at,並且使用V2 table
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

initdata.set_test_data(env, test_parameter)
    

class TestGetGiftCategory():
    gctype = ['live_room', 'liveshow', 'post_gift', 'instant_message']
    @pytest.fixture(scope='function')
    def initDB(self):
        sqlList = ["update gift_v2 set is_active = 1, delete_at is NULL"]
        sqlList.append("update gift_category_v2 set start_time = NULL, end_time = NULL, is_active = 1, delete_at is NULL")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
    
    def setCondition(self, categoryId, isActive, isDelete, isDelOfCategory, isExpiredOfCategory):
        if not isActive:
            sqlList = ["update gift_v2 set is_active = 0 where category_id = " + str(categoryId)]
        elif isDelete:
            sqlList = ["update gift_v2 set delete_at = '" + (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + "' where category_id = " + str(categoryId)]
        elif isDelOfCategory:
            sqlList = ["update gift_category_v2 set delete_at = '" + (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + "' where category_id = " + str(categoryId)]
        elif isExpiredOfCategory:
            sqlList = ["update gift_category_v2 set end_time = '" + (datetime.today() - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S') + "' where category_id = " + str(categoryId)]
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("test_input, categoryId, isActive, isDelete, isDelOfCategory, isExpiredOfCategory, expected", [
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], 3], 64, True, False, False, False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 3], 76, False, False, False, False,2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 3], 92, True, True, False, False,2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 3], 76, True, False, True, False,2), 
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], 3], 64, True, False, False, True, 2),
        ([test_parameter['err_token'], test_parameter['err_nonce'], 3], 92, True, False, False, True, 4)
    ])
    def testAuthAndType(self, test_input, categoryId, isActive, isDelete, isDelOfCategory, isExpiredOfCategory, expected):
        #驗證權限及查詢類別
        TimeCondition1 = (datetime.today() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        TimeCondition2 = (datetime.today() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        apiName = '/api/v2/identity/gift/list?giftCategoryId=' + str(test_input[2]) + '&item=20&page=1'
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        time.sleep(30)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)    
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            if  test_input[2] < 4:
                sql = "select g.id, g.category_name, g.point, g.thumb_url, g.url, g.multiple, order_seq from gift_v2 g "
                sql += "where g.category_id in (select id from gift_category_v2 where type = '" + self.gctype[test_input[2] - 1] + "' and  delete_at is Null and "
                sql += "((start_time <= '" + TimeCondition1 + "' or start_time is null) and (end_time >= '" + TimeCondition2 + "' or end_time is null)) "
                sql += "and is_active = 1 and delete_at is Null order by g.point"
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
