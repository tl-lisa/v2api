import json
import requests
import string
import time
from ..assistence import api

header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
def createPhoto(token, nonce, prefix, photo_url, repeatTimes):
    #print('createPhoto')
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    for i in range(repeatTimes):
        time.sleep(1)
        content = 'test info ' + str(i) 
        body = {'photoPath': photo_url,  'content': content} 
        api.add_photopost(prefix, header, body)
        #print(res.status_code)


def getPhotoList(token, nonce, prefix, liveMasterid):
    photoId = []
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    res = api.get_photo_list(prefix, header, liveMasterid, '10', '1')
    restext = json.loads(res.text)
    #print(restext)
    for i in restext['data']:
        photoId.append(i['id'])
    return(photoId)


def sendPhotoGift(token, nonce, prefix, photoId, giftId):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/identity/sendGift'
    body = {'giftId': giftId, 'postId': photoId}
    api.apiFunction(prefix, header, apiName, 'post', body)


def likePhoto(token, nonce, prefix, photoId, likenum):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    body = {'likes': likenum}
    apiName = '/api/v2/liveMaster/photoPost/' + photoId + '/like'         
    api.apiFunction(prefix, header, apiName, 'post', body) 


def addComment(token, nonce, prefix, photoId, comment):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/liveMaster/photoPost/' + photoId + '/comment'
    body = {'comment' : comment}
    api.apiFunction(prefix, header, apiName, 'post', body)