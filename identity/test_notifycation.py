#milestone20 #954
    # 取得個人通知訊息改用offset判斷，每次固定回傳20筆；
    # 不足20筆則無offset的資訊；若代入的offset超過則回傳空的list
    # /v2/identity/{{uid}}/notification/listMore (method:post)
import json
import requests
import pymysql
import time
import string
import threading
import socket
import pytest
from assistence import chatlib
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import sundry
from assistence import photo
from pprint import pprint

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
photoList = [
    'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png',
    'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/537c11b848cd11ea83b942010a8c0017.png',
    'https://d3eq1e23ftm9f0.cloudfront.net/namecard/photo/19ea53de35da11eab44842010a8c0fcc.jpg',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/001eccadc7221ace4accca2a99aa7cdb.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/4ad67dc80ee05690fb48c928c51579a4.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/f807f0145859c2b75e61ab566cd8e07b.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/b3e493f4116eea464f7a93ef480766f0.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/3b68522806a4cb7da102ae5ee54b52e7.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/c9cea222bd2e38026d72118917908677.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/3d6d9a5e64f73d33bb09b4d1870120ae.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/b8e71e6d37f7bff0ce6009917269df28.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/47e573e328d4d5ceef43919648834614.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/8fd3ceb375d060e2dc14963011892cf4.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/7b4372e062b3b70d5c08ff4f1f723ce0.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/npcAnimation/cd6611bddb64a579937bb184c158be4a.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/eventBanner/36ad90c35c4b87cd91ff3f5030b62897.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/2746f1d8981c44e3896bcdc3994903b7.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/5c139dbc12fdb7a96c3df011457b22b8.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/d866ce728c6dd4703c11de9416ff0c0e.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/f6cee6062354e3d7f0a8da71f7450d66.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/a29a9852b6577093aeb8ce8c003db158.png',
    'https://d1a89d7jvcvm3o.cloudfront.net/gift/b09b6ea4fdaff2a14c4c5d138fa5fbaf.png'
]

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearFansInfo(test_parameter['db'])
    initdata.clearPhoto(test_parameter['db'])
    initdata.clearNotiySetting(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [
        test_parameter['broadcaster_acc'], test_parameter['user_acc'], test_parameter['user1_acc']], idList)
    

#token, nonce是帶檢查收到通知的人
#scenario, identity, uid, isTrack, isPost, isComment, isSendPost, isOnAir, token, nonce, description, content, link, expected
testData = [
    ('track and black', 'livemaster', 0, 'track', 'broadcaster_token', 'broadcaster_nonce', 'TRACK_MASTER_REQUEST', '追蹤了你', '/user/', 2),
    ('post photo', 'fans', 1, 'post', 'user_token', 'user_nonce', 'MASTER_POST_PHOTO', '在初樂與你分享他的生活', '/post/', 2),
    ('post photo', 'black', 2, '', 'user1_token', 'user1_nonce', 'MASTER_POST_PHOTO', '在初樂與你分享他的生活', '/post/', 2),
    ('comment at photo', 'brocaster', 0, 'comment', 'broadcaster_token', 'broadcaster_nonce', 'COMMENT_REPLY_TO_USER', '留言給你', '/post/', 2),
    ('send gift', 'brocaster', 0, 'sendPost', 'broadcaster_token', 'broadcaster_nonce', 'MASTER_PHOTO_RECEIVE_GIFT', '送了 洪荒之力(1000)給你的動態', '/post/', 2),
    ('livemaster on air', 'fans', 1, 'onAir', 'user_token', 'user_nonce', 'MASTER_ON_LIVE', '熱烈開播中，快來支持你最愛的他！', '/room/', 2),
    ('livemaster on air', 'black', 2, '', 'user1_token', 'user1_nonce', 'MASTER_ON_LIVE', '熱烈開播中，快來支持你最愛的他！', '/room/', 2)
]

def setTrackingAndBlock():
    #print('track')
    authInfo  = [{'token': 'user_token', 'nonce': 'user_nonce'}, {'token': 'user1_token', 'nonce': 'user1_nonce'}]
    urlName = '/api/v2/identity/track'
    body = {"liveMasterId": idList[0]}
    for i in range(len(authInfo)):
        header['X-Auth-Token'] = test_parameter[authInfo[i]['token']]
        header['X-Auth-Nonce'] = test_parameter[authInfo[i]['nonce']]
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    urlName = '/api/v2/liveMaster/blockUser'
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    body = {'userId': idList[2]}
    api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)  
    return

def postPhoto():
    #print('postPhoto')
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
    for i in range(len(photoList)):
        body = {'photoPath': photoList[i],  'content': '第' + str(i) + '動態分享'} 
        api.add_photopost(test_parameter['prefix'], header, body)
    return

def postComment():
    #print('postComment')
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    res = api.get_photo_list(test_parameter['prefix'], header, idList[0], '20', '1')
    if res.status_code == 200:
        restext = json.loads(res.text)           
        pid = str(restext['data'][0]['id'])
        header['X-Auth-Token'] = test_parameter['user_token']
        header['X-Auth-Nonce'] = test_parameter['user_nonce']
        comment = '粉絲新增動態評論-一般使用者'
        res = api.add_photo_comment(test_parameter['prefix'], header, pid, comment) 
        print('pid= %s'%pid) 
        print('comment=%s'%res.status_code)
        pprint(json.loads(res.text))
    return

def sendGift():
    #print('sendGift')
    sqlList = ["update remain_points set remain_points = 2000 where identity_id = '" + idList[1] + "'"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    photoId = photo.getPhotoList(test_parameter['user_token'], test_parameter['user_nonce'] , test_parameter['prefix'], idList[0])
    photo.sendPhotoGift(test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['prefix'], photoId[0], 888)
    return

def onAir():
    #print('onAir')
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
    rid, chatlib, sock = sundry.Openroom(test_parameter['prefix'], header, 5, False, 0, '608行開播', 5)
    time.sleep(2)
    chatlib.leave_room(rid, sock)
    return

'''
黑名單的粉絲收不到該直播主的通知
有粉絲追蹤時直播主會收到推播及通知
直播主發佈動態時，粉絲會收到推播及通知
直播主的動態有人發表評論時，直播主會收到推播及通知
粉絲若送禮給該則動態，則直播主會收到推播及通知
直播主若開播，則粉絲會收到推播及通知
每次通知以offset判斷需不需要再撈取第二次
若不足20則，則無offset此參數
若offset大於該通知數量則回[]
'''
@pytest.mark.parametrize('scenario, identity, uid, action, token, nonce, description, content, link, expected', testData)
def testNofitycation(scenario, identity, uid, action, token, nonce, description, content, link, expected):
    funDic = {
        'track': setTrackingAndBlock,
        'post': postPhoto,
        'comment': postComment,
        'sendPost': sendGift,
        'onAir': onAir
    }
    funDic[action]() if action != '' else None    
    time.sleep(30)
    header['X-Auth-Nonce'] = test_parameter[nonce]
    header['X-Auth-Token'] = test_parameter[token]    
    urlName = '/api/v2/identity/' + idList[uid] +'/notification/listMore'
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'get',None)
    restext = json.loads(res.text)
    assert res.status_code // 100 == expected
    if identity == 'black':
        restext['data'] == []
    else:
        assert restext['data'][0]['action'] == description
        assert restext['data'][0]['content'] == content
        assert link in restext['data'][0]['link'] 
        if len(restext['data']) < 20:
            assert 'offset' not in restext
        elif (len(restext['data']) >= 20):
            offset = restext['offset']
            res1 = api.apiFunction(test_parameter['prefix'], header, urlName + '?offset=' + str(offset), 'get', None)
            restext1 = json.loads(res1.text)
            assert res1.status_code // 100 == 2
            assert restext['data'] != restext1['data']
       