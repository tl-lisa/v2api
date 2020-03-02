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
    auth_json = json.dumps(auth) + '\r\n'
    sock.send(auth_json.encode('utf-8'))
    check_event(sock)
    return


def join_room(rid, fpath, sock):
    flag = False
    room = {'action': 'IN_ROOM', 'data': {'roomId': 0}}
    room['data']['roomId'] = rid
    room_json = json.dumps(room) + '\r\n'
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
    room_json = json.dumps(room) + '\r\n'
    sock.send(room_json.encode('utf-8'))
    return


def send_message(strmsg, rid, sock):
    msg = {'action': 'MESSAGE', 'data': {'roomId': 0, 'content': ''}}
    msg['data']['roomId'] = rid
    msg['data']['content'] = strmsg
    msg_json = json.dumps(msg) + '\r\n'
    sock.send(msg_json.encode('utf-8'))
    return


def send_gift(sock, gift_id, broadcastid):
    gift = {'action': 'GIFT', 'data': {'giftId': '', 'userId': '', 'count': 1}}
    gift['data']['giftId'] = gift_id
    gift['data']['userId'] = broadcastid
    gift_json = json.dumps(gift) + '\r\n'
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
    keep_json = json.dumps(keep) + '\r\n'
    sock.send(keep_json.encode('utf-8'))
    receive_data = sock.recv(2048).decode('utf-8', errors='ignore')
    if receive_data.find('error') > 0:
        result = 1
    elif receive_data.find('ROOM_EXITED') > 0:
        print('Room_Exited %s' % time.localtime())
        result = 2
    return(result, receive_data)


def new_room(sock, roomtitle):
    new = {'action': 'NEW_ROOM', 'data': {'title': roomtitle}}
    new_json = json.dumps(new) + '\r\n'
    sock.send(new_json.encode('utf-8'))
    sock.recv(2048).decode('utf-8', errors='ignore')     
    rid = 0 
    while 1:
        check = check_event(sock)
        check1 = json.loads(check[1])
        if check1['event'] == 'RESPONSE':
            print('中華 RESPONSE: %s'%check1)
        elif check1['event'] == 'ROOM_NEW':
            print('中華 ROOM_NEW: %s'%check1)
            rid = check1['data']['roomId']
        elif check1['event'] == 'ROOM_IN':
            print('中華 ROOM_IN: %s'%check1)
        if rid > 0:        
            break
    return rid


def enterZego(sock, roomId):
    new = {'action': 'ENTER_ZEGO_ROOM', 'data': {'roomId': roomId}}
    new_json = json.dumps(new) + '\r\n'
    sock.send(new_json.encode('utf-8'))
    sock.recv(2048).decode('utf-8', errors='ignore')     
    while 1:
        check = check_event(sock)
        check1 = json.loads(check[1])
        if check1['event'] == 'ROOM_IN':
            print('ROOM_in: %s'%check1)  
            break 
        else:
            print('check1=%s'%check1)       
    return check1['data']['roomId']