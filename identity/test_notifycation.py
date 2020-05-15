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
photoList = ['https://d3eq1e23ftm9f0.cloudfront.net/story/photo/f7e2672253c511eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/e2af3e6253c411eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/b436d9c653bc11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/9d4f93f653bc11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/01cab01652ed11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/c882b1aa67fa11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/7f49c4c467fa11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/f6b4993267f811eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/47f36c6e592711eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/3bc4c6b8592711eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/fa606b0c587a11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/2ba963246def11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/1a0b5cd06def11eab44842010a8c0fcc.jpg', 
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/fb433e626dee11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/e76c33a86dee11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/0f001c1c6d9b11eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/f9854bb06d9911eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/f50d98b06cf111eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/e1ce5d146cd511eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/55563f766a9311eab44842010a8c0fcc.jpg',
            'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/e8237afa6a9111eab44842010a8c0fcc.jpg'
        ]

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearFansInfo(test_parameter['db'])
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']         
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))
    

#token, nonce是帶檢查收到通知的人
#scenario, identity, uid, isOffset, isTrack, isPost, isComment, isSendPost, isOnAir, token, nonce, action, content, link, expected
testData = [
    ('track and black', 'livemaster', idList[0], True, True, False, False, False, False, 'broadcaster_token', 'broadcaster_nonce', 'TRACK_MASTER_REQUEST', '追蹤了你', '/user/', 2),
    ('post photo', 'fans', idList[1], False, False, True, False, False, False, 'user_token', 'user_nonce', 'MASTER_POST_PHOTO', '在初樂與你分享他的生活', '/post/', 2),
    ('post photo', 'black', idList[2], False, False, True, False, False, False, 'user_token', 'user_nonce', 'MASTER_POST_PHOTO', '在初樂與你分享他的生活', '/post/', 2),
    ('comment at photo', 'brocaster', idList[0], False, False, False, True, False, False, 'broadcaster_token', 'broadcaster_nonce', 'COMMENT_REPLY_TO_USER', '留言給你', '/post/', 2),
    ('send gift', 'brocaster', idList[0], False, False, False, False, True, False, 'broadcaster_token', 'broadcaster_nonce', 'MASTER_PHOTO_RECEIVE_GIFT', '送了Mr.主人(1000)給你的動態', '/post/', 2),
    ('livemaster on air', 'fans', idList[1], False, False, False, False, False, True, 'broadcaster_token', 'broadcaster_nonce', 'MASTER_ON_LIVE', '熱烈開播中，快來支持你最愛的他！', '/room/', 2),
    ('livemaster on air', 'black', idList[2], False, False, False, False, False, True, 'broadcaster_token', 'broadcaster_nonce', 'MASTER_ON_LIVE', '熱烈開播中，快來支持你最愛的他！', '/room/', 2)
]

def setTrackingAndBlock():
    authInfo  = [{'token': 'user_token', 'nonce': 'user_nonce'}, {'token': 'user1_token', 'nonce': 'user1_nonce'}]
    urlName = '/api/v2/identity/track'
    body = {"liveMasterId": idList[0]}
    for i in range(len(authInfo)):
        header['X-Auth-Token'] = authInfo[i]['token']
        header['X-Auth-Nonce'] = authInfo[i]['nonce'] 
        api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
    time.sleep(2)
    urlName = '/api/v2/liveMaster/blockUser'
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']
    body = {'userId': idList[2]}
    api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)  
    return

def postPhoto():
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']   
    for i in range(len(photoList)):
        body = {'photoPath': photoList[i],  'content': '第' + str(i) + '動態分享'} 
        api.add_photopost(test_parameter['prefix'], header, body)
    return

def postComment():
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
        time.sleep(1)
    return

def sendGift():
    sqlList = ["update remain_points set remain_points = 1000 where identity_id = '" + idList[1] + "'"]
    dbConnect.dbSetting(test_parameter['db'], sqlList)
    photoId = photo.getPhotoList(test_parameter['broadcaster_token'], test_parameter['broadcaster_nonce'] , test_parameter['prefix'], idList[0])
    photo.sendPhotoGift(test_parameter['user_token'], test_parameter['user_nonce'], test_parameter['prefix'], photoId[0], 888)
    return

def onAir():
    header['X-Auth-Token'] = test_parameter['broadcaster_token']
    header['X-Auth-Nonce'] = test_parameter['broadcaster_nonce']    
    sundry.Openroom(test_parameter['prefix'], header, 5, False, 0, '608行開播', 5)
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
@pytest.mark.parameterize('scenario, identity, uid, isOffset, isTrack, isPost, isComment, isSendPost, isOnAir, token, nonce, action, content, link, expected', testData)
def testNofitycation(scenario, identity, uid, isOffset, isTrack, isPost, isComment, isSendPost, isOnAir, token, nonce, action, content, link, expected):
    if isTrack:
        setTrackingAndBlock()
    if isPost:
        postPhoto()
    if isComment:
        postComment()
    if isSendPost:
        sendGift()
    if isOnAir:
        onAir()
    urlName = '/api/v2/identity/' + uid +'/notification/list'
    res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', {})
    assert res.status_code // 100 == expected
    restext = json.loads(res.text)
    if identity == 'black':
        restext['data'] == []
    else:
        assert restext['data'][0]['action'] == action
        assert restext['data'][0]['content'] == content
        assert link in restext['data'][0]['link'] 
        if len(restext['data']) < 20:
            assert 'offset' not in restext
        elif (len(restext['data']) >= 20):
            offset = restext['offset']
            body = { "offset": offset}
            res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
            assert res.status_code // 100 == 2
        elif isOffset:
            res = api.apiFunction(test_parameter['prefix'], header, urlName, 'post', body)
            assert res.status_code // 100 == 2
            restext = json.loads(res.text)
            assert restext['data'] == []