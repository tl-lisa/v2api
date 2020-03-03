#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# encoding: utf-8
import json
import time
from pprint import pprint

def chat_room_auth(sock, header):
    auth = {'action': 'AUTH','data': {'token': '', 'nonce': ''}}
    auth['data']['token'] = header['X-Auth-Token']
    auth['data']['nonce'] = header['X-Auth-Nonce']
    auth_json = json.dumps(auth) + '\n' #跳脫字元由'\r\n' 改為 '\n
    sock.send(auth_json.encode('utf-8'))
    check_event(sock)
    return


def join_room(rid, fpath, sock):
    flag = False
    room = {'action': 'IN_ROOM', 'data': {'roomId': 0}}
    room['data']['roomId'] = rid
    room_json = json.dumps(room) + '\n'
    sock.send(room_json.encode('utf-8'))
    result_info = check_event(sock)
    if result_info[1].find('error') > 0:        
        flag = True
    else:
        wait_flag = True
        start_time = int(time.time())
        while wait_flag:
            result_info = check_event(sock)
            if result_info[1].find('ROOM_IN'):
                wait_flag = False
            else:
                current_time = int(time.time())
                if (current_time - start_time) > 30:                    
                    flag = True
                    break
    return(flag)


def leave_room(rid, sock):
    room = {'action': 'LEAVE_ROOM', 'data': {'roomId': 0}}
    room['data']['roomId'] = rid
    pprint(room)
    room_json = json.dumps(room) + '\n'
    sock.send(room_json.encode('utf-8'))
    return


def send_message(strmsg, rid, sock):
    msg = {'action': 'MESSAGE', 'data': {'roomId': 0, 'content': ''}}
    msg['data']['roomId'] = rid
    msg['data']['content'] = strmsg
    msg_json = json.dumps(msg) + '\n'
    sock.send(msg_json.encode('utf-8'))
    return


def send_gift(sock, gift_id, broadcastid):
    gift = {'action': 'GIFT', 'data': {'giftId': '', 'userId': '', 'count': 1}}
    gift['data']['giftId'] = gift_id
    gift['data']['userId'] = broadcastid
    gift_json = json.dumps(gift) + '\n'
    sock.send(gift_json.encode('utf-8'))
    return


def check_event(sock):
    receive_data = sock.recv(2048).decode('utf-8', errors='ignore')
    if receive_data.find('error') > 0:
        result = 3
    elif receive_data.find('ROOM_EXITED') > 0:
        result = 1
    else:
        result = 2
    return(result, receive_data)


def keep_live(sock):
    result = 0
    keep = {'action': 'PING'}
    keep_json = json.dumps(keep) + '\n'
    sock.send(keep_json.encode('utf-8'))
    receive_data = sock.recv(2048).decode('utf-8', errors='ignore')
    if receive_data.find('error') > 0:
        result = 1
    elif receive_data.find('ROOM_EXITED') > 0:
        print('Room_Exited %s' % time.localtime())
        result = 2
    return(result, receive_data)


def new_room(sock, roomtitle):
    strList = []
    isContinue = True    
    new = {'action': 'NEW_ROOM', 'data': {'title': roomtitle}}
    new_json = json.dumps(new) + '\n'
    sock.send(new_json.encode('utf-8'))
    sock.recv(2048).decode('utf-8', errors='ignore')     
    while isContinue:
        check = check_event(sock)
        strList = check[1].split('\n')
        #pprint(strList)
        for i in strList:
            if len(i)  > 0:
                check1 = json.loads(i)
                #pprint(check1)
                if check1['event'] == 'ROOM_IN':
                    pprint('ROOM_in: %s'%check1['data'])  
                    roomId = check1['data']['roomId']
                    isContinue = False 
    return roomId


def enterZego(sock, roomId):
    strList = []
    isContinue = True
    new = {'action': 'ENTER_ZEGO_ROOM', 'data': {'roomId': roomId}}
    #new_json = json.dumps(new) + '\r\n'
    new_json = json.dumps(new) + '\n'
    sock.send(new_json.encode('utf-8'))
    sock.recv(2048).decode('utf-8', errors='ignore')     
    while isContinue:
        check = check_event(sock)
        strList = check[1].split('\n')
        #pprint(strList)
        for i in strList:
            if len(i)  > 0:
                check1 = json.loads(i)
                #pprint(check1)
                if check1['event'] == 'ROOM_IN':
                    pprint('ROOM_in: %s'%check1['data'])  
                    roomId = check1['data']['roomId']
                    isContinue = False 
    return roomId