#/api/v2/identity/giftCategory/list?type=
#mileston 18 加入軟刪及判斷delete_at,並且使用V2 table
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
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}

initdata.set_test_data(env, test_parameter)

class TestGetGiftCategory():
    gctype = ['live_room', 'liveshow', 'post_gift', 'instant_message']

    @pytest.fixture(scope='class')
    def initDB(self):
        sqlList = ["update gift_category_v2 set start_time = NULL, end_time = NULL, is_active = 1, delete_at is NULL"]
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    def setData(self, startTime, endTime, isDelete):
        sqlList = []
        startTimeStr = ''
        endTimeStr = ''

        if startTime == 'Null':
            startTimeStr = 'start_time = NULL'
        elif startTime == 'small':
            startTimeStr = "start_time = '" + (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') + "'"
        elif startTime == 'bigger':
            startTimeStr = "start_time = '" + (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') + "'"

        if endTime == 'Null':
            endTimeStr = 'end_time = NULL'
        elif endTime == 'small':
            endTimeStr = "end_time = '" + (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') + "'"
        elif endTime == 'bigger':
            endTimeStr = "end_time = '" + (datetime.today() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S') + "'"

        sqlStr = "update gift_category_v2 set " + startTimeStr + ", " +  endTimeStr
        if isDelete:
            sqlStr += ", delelet_at = '" + (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S') + "'"
        #print(sqlStr)
        sqlList.append(sqlStr)
        dbConnect.dbSetting(test_parameter['db'], sqlList)

    @pytest.mark.parametrize("test_input, startTime, endTime, isDelete, expected",[ 
        ([test_parameter['backend_token'], test_parameter['backend_nonce'], 1], 'Null', 'Null', False, 2),
        ([test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'], 3], 'Null', 'small', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'Null', 'bigger', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'small', 'Null', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'bigger', 'Null', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'small', 'small', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'bigger', 'bigger', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'small', 'bigger', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 4], 'bigger', 'small', False, 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 5], 'small', 'bigger', False, 5), #送exception到sentry.
        ([test_parameter['err_token'], test_parameter['err_nonce'], 1], 'small', 'bigger', False,4)
    ])
    def testGetCategory(self, test_input, startTime, endTime, isDelete, expected):
        TimeCondition1 = (datetime.today() - timedelta(minutes=1)).strftime('%Y-%m-%d  %H:%M:%S')
        TimeCondition2 = (datetime.today() + timedelta(minutes=1)).strftime('%Y-%m-%d  %H:%M:%S')
        #驗證權限及查詢類別
        self.setData(startTime, endTime, isDelete)
        apiName = '/api/v2/identity/giftCategory/list?type=' + str(test_input[2]) + '&item=30&page=1'
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]
        time.sleep(60)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)  
        restext = json.loads(res.text)
        #pprint(restext)  
        assert res.status_code // 100 == expected
        if expected == 2:
            if  test_input[2] < 5:
                sql = "select id, name, banner, url, start_time, end_time from gift_category_v2 where type = '" + self.gctype[test_input[2] - 1] + "' and  deleted_at is null and "
                sql += "((start_time <= '" + TimeCondition1 + "' or start_time is null) and (end_time >= '" + TimeCondition2 + "' or end_time is null)) order by id desc"
                dbResult = dbConnect.dbQuery(test_parameter['db'], sql)
                #pprint(dbResult)
                assert restext['totalCount'] == len(dbResult)
                if restext['totalCount'] > 0:
                    for i in range(len(dbResult)):
                        #print('i = %d; data id = %d; db id = %d'%(i, restext['data'][i]['id'], dbResult[i][0]))
                        assert restext['data'][i]['id'] == dbResult[i][0]
                        assert restext['data'][i]['type'] == test_input[2]
                        assert restext['data'][i]['categoryName'] == dbResult[i][1]
                        assert restext['data'][i]['banner'] in ('', dbResult[i][2])
                        assert restext['data'][i]['url'] in ('', dbResult[i][3])
            else:
                assert restext['totalCount'] == 0
