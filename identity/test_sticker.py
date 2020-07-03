#milestone25 使用者取得動態表情貼(只抓status=ture)
import json
import requests
import pymysql
import time
import string
import threading
import socket
import pytest
import datetime
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from assistence import sundry

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
liveMasterList = []

Msg = {
    200:{'Status': 'Ok', 'Message': 'SUCCESS'},
    401:{'Status': 'Error', 'Message': '使用者驗證錯誤，請重新登入'},
    403:{'Status': 'Error', 'Message': 'PERMISSION_REQUIRED'},
    400:{'Status': 'Error', 'Message': 'PARAM_ERROR'},
    406:{'Status': 'Error', 'Message': 'LACK_OF_NECESSARY_PARAMS'},
    404:{'Status': 'Error', 'Message': ['GIFT_CATAGORY_NOT_FOUND', 'MEDIA_NOT_FOUND']}
}

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearSticker(test_parameter['db'])

        #scenario, token, nonce, action, table, index, condition, resList, expected
testData=[
    ('新增sticker及sticker_group資料status=true，且指定group','user_token', 'user_nonce', 'insert', ['sticker_group', 'sticker'], 0, '?groupId=1', [1], 200),
    ('新增sticker資料sttus=false，且指定group','user_token', 'user_nonce', 'insert', ['sticker'], 1, '?groupId=1', [1], 200),
    ('新增sticker及sticker_group資料status=false，不指定group','backend_token', 'backend_nonce', 'insert', ['sticker_group', 'sticker'], 2, '', [1], 200),
    ('新增sticker資料status=true，不指定group','broadcaster_token', 'broadcaster_nonce', 'insert', ['sticker'], 3, '', [1], 200),
    ('新增sticker及sticker_group資料status=true，不指定group','broadcaster_token', 'broadcaster_nonce', 'insert', ['sticker_group', 'sticker'], 4, '', [1, 3], 200),
    ('新增sticker資料status=true但已被刪除，不指定group','broadcaster_token', 'broadcaster_nonce', 'insert', ['sticker'], 5, '', [1, 3], 200),
    ('指定groupId存在但為false','user_token', 'user_nonce', '', [], 1, '?groupId=2', [1], 400),
    ('指定groupId不存在','user_token', 'user_nonce', '', [], 1, '?groupId=12', [1], 400),
    ('有給groupIdo做條件，但未指定groupId','user_token', 'user_nonce', '', [], 1, '?groupId=', [1], 400),
    ('token/nonce不存在','err_token', 'err_nonce', '', [], 1, '?groupId=2', [1], 401)
]
class TestSticker():
    result = {
        1:[1, 'smile1', 'https://smile1.jpg', 'https://smile1.webp'],
        3:[5, 'happy1', 'https://happy1.jpg', 'https://happy1.webp']
    }

    sticker = [
        "group_id = 1, name='smile1', image_url = 'https://smile1.jpg', animation_url = 'https://smile1.webp', status = 1",
        "group_id = 1, name='smile2', image_url = 'https://smile2.jpg', animation_url = 'https://smile2.webp', status = 0",
        "group_id = 2, name='cry1', image_url = 'https://cry1.jpg', animation_url = 'https://cry1.webp', status = 1",
        "group_id = 2, name='cry2', image_url = 'https://cry2.jpg', animation_url = 'https://cry2.webp', status = 0",
        "group_id = 3, name='happy1', image_url = 'https://happy1.jpg', animation_url = 'https://happy1.webp', status = 1",
        "group_id = 1, name='smile3', image_url = 'https://smile3.jpg', animation_url = 'https://smile3.webp', status = 1, deleted_at = '2020-06-29 19:10:45'"
    ]
    sticker_group = [
        "name='smile', status = 1", 
        "", 
        "name='cry', status = 0", 
        "", 
        "name='happy', status = 1",
        ""
    ]
    def setup_method(self):
        sundry.clearCache(test_parameter['db'])
        
    def insertData(self, table, index):
        sqlList = []
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in table:            
            sqlStr = "insert into " + i + " set "
            if i == 'sticker_group':
                sqlStr += self.sticker_group[index]
            else:
                sqlStr += self.sticker[index]
            sqlStr += ", created_at='" + now + "', updated_at=' "  + now + "', create_user_id='lisa', update_user_id='lisa'"
            sqlList.append(sqlStr)
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        
    @pytest.mark.parametrize("scenario, token, nonce, action, table, index, condition, resList, expected", testData)
    def testGetSticker(self, scenario, token, nonce, action, table, index, condition, resList, expected):
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/identity/sticker/list' + condition
        self.insertData(table, index) if action != '' else None            
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'get', None)
        restext = json.loads(res.text)
        assert res.status_code == expected
        assert restext['Status'] == Msg[expected]['Status']
        assert restext['Message'] in Msg[expected]['Message']
        if expected == 200:
            for i in restext['data']:
                k = i['stickerGroupId']
                assert i['stickerGroupId'] in resList
                assert i['stickerId'] == self.result[k][0]
                assert i['name'] == self.result[k][1]
                assert i['imageUrl'] == self.result[k][2]
                assert i['animationUrl'] == self.result[k][3]