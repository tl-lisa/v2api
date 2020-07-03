import json
import requests
import string
import time
from . import api

header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
def createBody(typeDesc, photoPath, content, previewPath, videoPath, giftCategoryId):
    body = {}
    if typeDesc != '':
        body['type'] = typeDesc
    if giftCategoryId != '':
        body['giftCategoryId'] = int(giftCategoryId)
    body['photoPath'] = photoPath
    body['content'] = content
    body['videoPath'] = videoPath
    body['previewPath'] = previewPath
    return body

def createPhoto(token, nonce, prefix, body):
    apiName = '/api/v2/liveMaster/photoPost' 
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    res = api.apiFunction(prefix, header, apiName, 'post', body)
    return res
       

def getPhotoList(token, nonce, prefix, liveMasterid, items, pages):
    apiName = '/api/v2/liveMaster/' +liveMasterid + '/photoPost?item=' + str(items) + '&page=' + str(pages)
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    res = api.apiFunction(prefix, header, apiName, 'get', None)
    return res


def sendPhotoGift(token, nonce, prefix, photoId, giftId):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/identity/sendGift'
    body = {'giftId': giftId, 'postId': photoId}
    res = api.apiFunction(prefix, header, apiName, 'post', body)
    #print(json.loads(res.text))
    return res


def likePhoto(token, nonce, prefix, photoId, likenum):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    body = {'likes': likenum}
    apiName = '/api/v2/liveMaster/photoPost/' + photoId + '/like'         
    res = api.apiFunction(prefix, header, apiName, 'post', body) 
    return res


def addComment(token, nonce, prefix, photoId, comment):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/liveMaster/photoPost/' + str(photoId) + '/comment'
    body = {'comment' : comment}
    res = api.apiFunction(prefix, header, apiName, 'post', body)
    return res

def delPhoto(token, nonce, prefix, photoId):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/liveMaster/photoPost/' + photoId 
    res = api.apiFunction(prefix, header, apiName, 'delete', None)
    return res

def SpecificalPhoto(token, nonce, prefix, photoId):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/liveMaster/photoPost/' + str(photoId)
    res = api.apiFunction(prefix, header, apiName, 'get', None)
    return res

def updatePhoto(token, nonce, prefix, photoId, body):
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    apiName = '/api/v2/liveMaster/photoPost/' + str(photoId)
    res = api.apiFunction(prefix, header, apiName, 'put', body)
    return res