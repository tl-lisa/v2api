#mileston17 create '/api/v2/identity/sendGift' #775 
#mileston18 多加回傳欄位：postid #831
import json
import requests
import pymysql
import time
import pytest
import string
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from ..assistence import photo
from pprint import pprint

env = 'testing'
test_parameter = {}
idlist = []
testData = []
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
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
init()

def f():
    giftId = 100  #'234df236-8826-4938-8340-32f39df43ed1'; category=108(post_gift)
    giftId1 = 64  #'e5741caa-2924-4e22-a955-02a4f50f382d'; category=65(非post_gift)
    testData = []
    photoId = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idlist[0])
    testData = [([test_parameter['user_token'], test_parameter['user_nonce'], 10000, giftId, photoId[0]], 2),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 10000, giftId1, photoId[0]], 4),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 0, giftId, photoId[0]], 4),
        ([test_parameter['user_token'], test_parameter['user_nonce'], 10000, '1234454', photoId[0]], 4),    
        ([test_parameter['user_token'], test_parameter['user_nonce'], 10000, giftId, 0], 4),    
        ([test_parameter['err_token'], test_parameter['err_nonce'], 10000, giftId, photoId[0]], 4)
        ]
    return testData


class TestSendGiftToPhoto():
    giftUUID = '234df236-8826-4938-8340-32f39df43ed1' 
    photo.createPhoto(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], test_parameter['photo_url'], 3)
    photoId = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idlist[0])

    @pytest.mark.parametrize("test_input, expected", f())
    def testSendGift(self, test_input, expected):
        pprint(test_input)
        sqlList = []
        sqlList.append("update remain_points set remain_points = " + str(test_input[2]) + " where identity_id = '" + idlist[2] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
        if expected == 2:
            sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idlist[0] + "', '" + idlist[2]  + "') order by identity_id"     
            bfExperience = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        header['X-Auth-Token'] = test_input[0]
        header['X-Auth-Nonce'] = test_input[1]  
        apiName = '/api/v2/identity/sendGift'
        body = {'giftId': test_input[3], 'postId': test_input[4]}
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        pprint(json.loads(res.text))
        assert res.status_code // 100 == expected
        if expected == 2:
            restext = json.loads(res.text)
            assert restext['data']['pointLeft'] == 9000
            sqlStr = "select experience, identity_id from user_experience where identity_id in ('" + idlist[0] + "', '" + idlist[2]  + "') order by identity_id"     
            afExperience = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            for i in range(2):
                if bfExperience[i][1] == idlist[0]:
                    assert afExperience[i][0] - bfExperience[i][0] == 1000
                else:
                    assert afExperience[i][0] - bfExperience[i][0] == 3000
