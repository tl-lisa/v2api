import json
import requests
import string
import time
from pprint import pprint
from datetime import datetime, timedelta
from . import chatlib
from . import api
from . import dbConnect
from . import initdata

def createMember(prefix, token, nonce, memberList):
    liveMasterList = []
    initList =  ['liveAcc0011', 'liveAcc0012', 'liveAcc0013', 'liveAcc0014', 'liveAcc0015', 'liveAcc0016', 'liveAcc0017', 
        'liveAcc0018', 'liveAcc0019', 'liveAcc0020']
    initdata.initIdList(prefix, token, nonce, initList, liveMasterList)
    for i in range (len(liveMasterList)):
        info = {}
        info['id'] = liveMasterList[i]
        info['loginId'] = initList[i]
        info['nickname'] = '我是第' + str(i) + '號'
        info['thumbnail'] = 'https://imgur.com/GtnFNvk' + str(i) + '.png'
        memberList.append(info)

def createLiveshowBody(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList):
    if isExpired:
        bannerStartTime = int(time.mktime((datetime.today() - timedelta(days=3)).timetuple()))
        bannerEndTime = int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))
        liveStartTime = int(time.mktime((datetime.today() - timedelta(days=2) + timedelta(hours=4)).timetuple()))
        liveEndTime = int(time.mktime((datetime.today() - timedelta(days=2) + timedelta(hours=6)).timetuple()))
    else:
        bannerStartTime = int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))
        bannerEndTime = int(time.mktime((datetime.today() + timedelta(days=1)).timetuple()))
        liveStartTime = int(time.mktime((datetime.today() + timedelta(hours=4)).timetuple()))
        liveEndTime = int(time.mktime((datetime.today() + timedelta(hours=6)).timetuple()))
    body = {}
    teams = {}
    body['title'] = title
    body['bannerUrl'] = 'https://d1a89d7jvcvm3o.cloudfront.net/liveBanner/ee71287cdce0361935c1b045e58e1a8f.jpeg'
    body['bannerClickUrl'] = 'https://github.com/onlifemedia/tl-backend/wiki/%5Benhancement%5D-Liveshow-%E9%96%8B%E6%92%AD%E5%BB%BA%E7%BD%AE'
    body['liveBannerUrl'] = 'https://d1a89d7jvcvm3o.cloudfront.net/liveBanner/36d79ea932633b29b6d9fc5868c9e802.jpeg'
    body['bannerStartTime'] = bannerStartTime
    body['bannerEndTime'] = bannerEndTime
    body['liveStartTime'] = liveStartTime
    body['liveEndTime'] = liveEndTime
    body['type'] = liveshowType
    body['poolId'] = memberList[poolId]['id']
    body['giftCategory'] = giftCategory
    body['rtmpPullUrl'] = rtmpPullUrl
    for i in range(teams_num):
        temp = {}
        members = []
        for j in range(mumber_num):
            members.append(memberList[i * mumber_num + j])
        if isNameEmpty:
            temp['name'] = '' 
        else:
            temp['name'] = '第' + str(i + 1) + '組'
        temp['members'] = members            
        teams[str(i + 1)] = temp
    body['teams'] = teams
    #pprint(body)
    return body

def establish(prefix, db, header, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList, liveshowId):
    body = createLiveshowBody(title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList)
    #pprint(body)
    apiName = '/api/v2/backend/liveshow/establish'
    api.apiFunction(prefix, header, apiName, 'post', body)
    sqlStr = 'select max(id) from liveshow'
    result = dbConnect.dbQuery(db, sqlStr)
    liveshowId.append(result[0][0])
    return body


def liveshowPrepare(prefix, db, header, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList, liveshowId):
    body = establish(prefix, db, header, title, liveshowType, poolId, teams_num, mumber_num, giftCategory, rtmpPullUrl, isNameEmpty, isExpired, memberList, liveshowId)
    apiName = '/api/v2/backend/liveshow/prepare'
    body1 = {'liveshowId': liveshowId[0]}
    api.apiFunction(prefix, header, apiName, 'post', body1)
    return body

