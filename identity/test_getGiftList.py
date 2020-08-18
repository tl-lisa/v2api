#/api/v2/identity/gift/list?giftCategoryId=
#mileston 18 加入軟刪及判斷delete_at,並且使用V2 table, 點數由小到大排序
#milestone25 #1445 加入二個參數isMultiple：是否為連擊禮物；multiples：如果是可以連發的禮物，每點一次時變動的數量級距
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

def setup_module():
    initdata.set_test_data(env, test_parameter)
    
@pytest.fixture(scope='function')
def initDB():
    sqlList = ["update gift_v2 set is_active = 1, deleted_at = NULL"]
    sqlList.append("update gift_category_v2 set start_time = NULL, end_time = NULL, deleted_at = NULL")
    dbConnect.dbSetting(test_parameter['db'], sqlList)

class TestGetGiftCategory():
    gctype = ['live_room', 'liveshow', 'post_gift', 'instant_message']
    
    def setCondition(self, categoryId, isActive, isDelete, isDuriation, isExpired):
        sqlList = []
        result = dbConnect.dbQuery(test_parameter['db'], "select min(id) from gift_v2 where category_id = " + str(categoryId))
        if not isActive:          
            sqlStr = "update gift_v2 set is_active = 0 where id = "  + str(result[0][0])
        elif isDelete:
            sqlStr = "update gift_v2 set deleted_at = '" + (datetime.today() - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S') + "' where id = " + str(result[0][0])
        elif isDuriation:
            sqlStr  = "update gift_category_v2 set end_time = '" + (datetime.today() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S') 
            sqlStr += "', start_time = '" + (datetime.today() - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S') + "' where id = " + str(categoryId)
        elif isExpired:
            sqlStr = "update gift_category_v2 set end_time = '" + (datetime.today() - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S') + "' where id = " + str(categoryId)
        sqlList.append(sqlStr)
        dbConnect.dbSetting(test_parameter['db'], sqlList) if sqlList else None

    @pytest.mark.parametrize("scenario, token, nonce, typeNum, categoryId, isActive, isDelete, isDuriation, isExpired, expected", [
        ('該項禮物未上架', 'backend_token', 'backend_nonce', 1, 64, False, False, False, False, 2),
        ('該項禮物已被封存', 'user_token', 'user_nonce', 2, 76, False, True, False, False,2),
        ('該項禮物使用期間尚未開始(是以gift_category_v2)', 'broadcaster_token', 'broadcaster_nonce', 3, 119, True, False, True, False,2),
        ('禮物已過期(是以gift_category_v2)', 'user_token', 'user_nonce', 2, 92, True, False, False, True,2), 
        ('權限不正確', 'err_token', 'err_nonce', 1, 92, True, False, False, True, 4)
    ])
    def testAuthAndType(self, initDB, scenario, token, nonce, typeNum, categoryId, isActive, isDelete, isDuriation, isExpired, expected):
        #驗證權限及查詢類別
        self.setCondition(categoryId, isActive, isDelete, isDuriation, isExpired)
        TimeCondition1 = (datetime.today() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        TimeCondition2 = (datetime.today() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        apiName = '/api/v2/identity/gift/list?giftCategoryId=' + str(categoryId) + '&item=20&page=1'
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        time.sleep(30)
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)    
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            sqlStr  = "select g.id, g.name, g.point, g.thumb_url, g.animation_url, g.is_multiple, g.uuid from gift_v2 g inner join gift_category_v2 c "
            sqlStr += "on g.category_id = c.id and c.id =  " + str(categoryId) + " "
            sqlStr += "and c.deleted_at is Null and ((c.start_time <= '" + TimeCondition1 + "' or c.start_time is null) "
            sqlStr += "and (c.end_time >= '" + TimeCondition2 + "' or c.end_time is null)) "
            sqlStr += "where g.is_active = 1 and g.deleted_at is Null order by g.id"
            dbResult = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            assert restext['totalCount'] == len(dbResult)
            if restext['totalCount'] > 0:
                for i in range(restext['totalCount']):
                    assert restext['data'][i]['id'] == dbResult[i][0]
                    assert restext['data'][i]['categoryId'] == categoryId
                    assert restext['data'][i]['name'] == dbResult[i][1]
                    assert restext['data'][i]['point'] == dbResult[i][2]
                    assert restext['data'][i]['thumbUrl'] == dbResult[i][3]
                    assert restext['data'][i]['url'] == dbResult[i][3]
                    assert restext['data'][i]['animationUrl'] == dbResult[i][4]
                    assert int(restext['data'][i]['isMultiple']) == dbResult[i][5]
                    assert restext['data'][i]['uuid'] == dbResult[i][6]
                    if restext['data'][i]['isMultiple']:
                        assert restext['data'][i]['multiples'] == [1, 20, 520, 999]
                    else:
                        assert restext['data'][i]['multiples'] == [1, 2, 4, 6, 8]
