#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import json
import requests
from pprint import pprint


def user_login(prefix, account, pwd):
    url = prefix + '/api/v2/identity/auth/login'
    body = {
        "account": account,
        "password": pwd,
        "pushToken": ''
    }
    #print(body)
    res = requests.post(url, json=body)
    #print(json.loads(res.text))
    if res.status_code // 100 == 2:
        restext = json.loads(res.text)
        return(restext)
    else:
        return(json.loads(res.text))


def user_login_1(prefix, account, pwd):
    url = prefix + '/api/v1/auth/login'
    body = {'loginId': account, 'password': pwd}
    res = requests.post(url, json=body)
    if res.status_code == 200:
        return(res)
    else:
        print('account %s login failed' % account)
        return(res)


def set_tracking(prefix, head, way, bid):
    url = prefix + '/api/v1/track/tracking/' + bid
    if way == 'post':       
        res = requests.post(url, headers=head, json={})
    else:
        #print(url)
        res = requests.delete(url, headers=head)
    return(res)


def get_personal_info(prefix, head):
    url = prefix + '/api/v1/personal/info'
    #print('url=%s' % url)
    res = requests.get(url, headers=head)
    if res.status_code != 200:
        json_result = ''
    else:
        json_result = json.loads(res.text)
    return(json_result)


def get_backend_user(prefix, head, id):
    url = prefix + '/api/v1/backend/user/' + id
    res = requests.get(url, headers=head)
    if res.status_code != 200:
        json_result = ''
    else:
        json_result = json.loads(res.text)
    return(json_result)


def register(prefix, account, header):
    url = prefix + '/api/v1/identity/register'
    body = {"loginId": account, 'password': '123456', 'publicSexInfo': False}
    requests.post(url, headers=header, json=body)
    #str1 = res.text
    #print(str1)
    return


def change_user_mode(prefix, id, mode, header):
    url = prefix + '/api/v2/backend/user/' + id
    #print(url)
    body = {'identityStatus': mode}
    requests.post(url, headers=header, json=body)
    #str1 = res.text
    #print(str1)
    return


def add_point(prefix, id, header):
    url = prefix + '/api/v1/identity/' + id + '/points'
    body = {'addPoints': 5000, 'ratio': 2, 'reason': 'testing'}
    requests.put(url, headers=header, json=body)
    #str1 = res.text
    return


def set_bank(prefix, bid, header):
    url = prefix + '/api/v1/identity/' + bid + '/account'
    body = {'accountNo': '0', 'bankName': '0', 'branchBank': '0', 'branchNo': '0'}
    res = requests.put(url, headers=header, json=body)
    if res.status_code != 200:
        str1 = res.text
        print(str1)
    return


def get_trackList(prefix, head):
    url = prefix + '/api/v1/personal/trackList/10/0'
    res = requests.get(url, headers=head)
    if res.status_code != 200:
        print(res.text)
        json_result = ''
    else:
        json_result = json.loads(res.text)
    return(json_result)


def search_user(prefix, account, header):
    url = prefix + '/api/v1/backend/identity/search'
    #print('account = %s' % account)
    body = {"input": account, "page": 0, "size": 10, "statuses": []}
    res = requests.post(url, headers=header, json=body)
    json_result = json.loads(res.text)
    #pprint(json_result)
    if json_result['totalCount'] > 1:
        for i in json_result['data']:
            if i['loginId'] == account:
                id = i['id']
                break
        return(id)
    else:
        return(json_result['data'][0]['id'])


def search_master(prefix, header, body, inum, pnum):
    url = prefix +  '/api/v1/identity/search/liveMaster/' + inum + '/' + pnum
    res = requests.post(url, headers=header, json=body)
    return(res)


def set_photo_like(prefix, header, pid):
    url = prefix +  '/api/v1/photo/like/' + pid
    res = requests.post(url, headers=header, json={})
    return(res)


def get_room_info(prefix, bid, header):
    room_info = {'roomId': 0, 'socketIp': '', 'socketPort': ''}
    url = prefix + '/api/v1/live/info/' + bid
    res = requests.get(url, headers=header)
    str1 = res.text
    if str1 != '':
        json_result = json.loads(str1)
        room_info['roomId'] = json_result['roomId']
        room_info['socketIp'] = json_result['socketIp']
        room_info['socketPort'] = json_result['socketPort']
    return(room_info)


def get_load_balance(prefix, header):
    url= prefix + '/api/v1/live/loadBalance/'
    #print(url)
    res = requests.get(url, headers=header)
    #print(res.status_code)
    if res.status_code != 200:
        json_result = ''
    else:
        json_result = json.loads(res.text)
    return(json_result)

#--------------------API V2-----------------#
def create_photo_comment(prefix, header1, pid, comment):
    url = prefix + '/api/v2/liveMaster/photoPost/' + pid + '/comment'
    body = {'comment' : comment}
    res = requests.post(url, headers=header1, json=body)
    return(res)

def backend_user(prefix, head, body, id):
    url = prefix + '/api/v2/backend/user/' + id
    res = requests.post(url, headers=head, json=body)
    return(res)


def yipay_init(prefix, body, header):
    url = prefix + '/api/v2/transaction/ypgateway/initiate'
    res = requests.post(url, headers=header, json=body)
    return(res)


def yipay_callback(prefix, body, header1):
    url = prefix + '/api/v2/transaction/ypgateway/result'
    header1['Content-Type'] = 'application/x-www-form-urlencoded'
    res = requests.post(url, headers=header1, data=body)
    return(res)


def set_onairtime(prefix, body, header1):
    url = prefix + '/api/v2/liveMaster/onAirTime'
    res = requests.post(url, headers=header1, json=body)
    return(res)


def get_onairtime(prefix, MasterId, header1):
    url = prefix + '/api/v2/liveMaster/' + MasterId + '/onAirTime'
    res = requests.get(url, headers=header1)
    return(res)


def del_onairtime(prefix, header1, type, id):
    url = prefix + '/api/v2/liveMaster/onAirTime/' + type + '/' + str(id)
    #print(url)
    res = requests.delete(url, headers=header1)
    return(res)


def set_namecard_like(prefix, header1, MasterId, num):
    url = prefix + '/api/v2/liveMaster/' + MasterId + '/like'
    body = {'likes': num}
    res = requests.post(url, headers=header1, json=body)
    return(res)


def namecard_operator(prefix, header1, method, MasterId, link_address):
    body = {'url': link_address} if method != 'get' else None
    res = apiFunction(prefix, header1, '/api/v2/liveMaster/' + MasterId + '/nameCard', method, body)
    return(res)


def del_cover(prefix, header1, card_id):
    url = prefix + '/api/v2/liveMaster/nameCard/' + str(card_id)
    res = requests.delete(url, headers=header1)
    return(res)


def update_cover(prefix, header1, card_id):
    url = prefix + '/api/v2/liveMaster/nameCard/cover/' + str(card_id)
    body = {}
    res = requests.put(url, headers=header1, json=body)
    return(res)


def upload_image(prefix, header1, filepath, file_name, file_addr):
    url = prefix + '/api/v2/cdn/' + filepath
    body = {'file': (file_name, open(file_addr, 'rb').read())}
    res = requests.post(url, headers=header1, files=body)
    return(res)


def get_comment_list(prefix, header1, post_id, inum, pnum):
    url = prefix + '/api/v2/liveMaster/photoPost/' + post_id + '/comment?item=' + str(inum) + '&page=' + str(pnum)
    res = requests.get(url, headers=header1)
    return(res)


def delete_comment(prefix, header1, post_id, comm_id):
    url = prefix + '/api/v2/liveMaster/photoPost/' + post_id + '/comment/' + comm_id
    res = requests.delete(url, headers=header1)
    return(res)


def get_fans_list(prefix, header1, mid, inum, pnum):
    url = prefix + '/api/v2/liveMaster/' + mid + '/fans?item=' + inum + '&page=' + pnum
    res = requests.get(url, headers=header1)
    return(res)


def get_gift_list(prefix, header1, way, mid, inum, pnum):
    url = prefix + '/api/v2/liveMaster/' + mid + '/gift/' + way + '?item=' + inum + '&page=' + pnum
    res = requests.get(url, headers=header1)
    return(res)


def add_livecontroller(prefix, header1, body):
    url = prefix + '/api/v2/liveMaster/liveController'
    res = requests.post(url, headers=header1, json=body)
    return(res)


def delete_livecontroller(prefix, header1, uid):
    url = prefix + '/api/v2/liveMaster/liveController/' + uid
    res = requests.delete(url, headers=header1)
    return(res)


def get_livecontroller(prefix, header1, mid, inum, pnum):
    url = prefix + '/api/v2/liveMaster/' + mid + '/liveController?item=' + inum + '&page=' + pnum
    res = requests.get(url, headers=header1)
    return(res)


def add_block_user(prefix, header1, body):
    url = prefix + '/api/v2/liveMaster/blockUser'
    #print(body)
    res = requests.post(url, headers=header1, json=body)
    return(res)


def delete_block_user(prefix, token, nonce, uid):
    header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    url = prefix + '/api/v2/liveMaster/blockUser/' + uid
    res = requests.delete(url, headers=header)
    return(res)


def get_block_user(prefix, header1, inum, pnum):
    url = prefix + '/api/v2/liveMaster/blockUser?item=' + inum + '&page=' + pnum
    res = requests.get(url, headers=header1)
    return(res)


def add_photo_comment(prefix, header1, pid, comment):   
    url = prefix + '/api/v2/liveMaster/photoPost/' + pid + '/comment'
    body = {'comment' : comment}
    res = requests.post(url, headers=header1, json=body)
    return(res)

def changeRole(prefix, token, nonce, idList, roleType):
    #5:一般用戶；4:直播主
    header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    url = '/api/v2/backend/user/role'
    body = {'ids': idList, 'role': roleType}
    res = apiFunction(prefix, header, url, 'patch', body)
    return(res)

def blockUser(prefix, token, nonce, userId):
    header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    url = '/api/v2/liveMaster/blockUser'
    body = {'userId': userId}
    res = apiFunction(prefix, header, url, 'post', body)
    return(res)

def apiFunction(prefix, head, apiName, way, body):
    resquestDic = {
        'post':requests.post,
        'put':requests.put,
        'patch':requests.patch, 
        'get':requests.get, 
        'delete':requests.delete}
    url = prefix + apiName  
    if body:
        head['Content-Type'] = 'application/json'
        res1 = resquestDic[way](url, headers=head, json=body)
    else: 
        if head.get('Content-Type'):
            del head['Content-Type']          
        res1 = resquestDic[way](url, headers=head)
    print(head)
    print('url = %s, method= %s'% (url, way))  
    print(body) if body else print('no body')
    pprint('status code = %d'%res1.status_code)
    pprint(json.loads(res1.text))
    return res1 
