import time
import socket
import paramiko
import base64
import hashlib
import json
from pprint import pprint
from datetime import datetime, timedelta
from . import chatlib
from . import api
from collections import OrderedDict
from Crypto.Cipher import AES


class Cryptor:
    def __init__(self, key, iv):
        self.key = base64.b64decode(key)
        self.iv = base64.b64decode(iv)

    def encrypt(self, string):
        string = self.pad(string)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(string))

    def decrypt(self, string):
        enc = base64.b64decode(string)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self.unpad(cipher.decrypt(enc))

    def sha1(self, string):
        s = hashlib.sha1()
        s.update(string)
        return s.hexdigest()

    def pad(self, s):
        BS = 16
        return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

def yipayencode(paramsData):
    jsonString = json.dumps(paramsData, separators=(',', ':'))  # 產出無空格的 JSON
    keyString = 'zBaw7bzzD8K1THSGoIbev08xEJp5yzyeuv1MWJDR2L0='  # AES Key，此為測試環境用，正式環境請替換為商家專用的 Key
    ivString = 'YeQInQjfelvkBcWuyhWDAw=='                       # AES IV，此為測試環境用，正式環境請替換為商家專用的 IV
    cryptor = Cryptor(keyString, ivString)
    encryptString = cryptor.encrypt(jsonString)
    checkCode = cryptor.sha1(encryptString)
    return(checkCode)

def yipay(prefix, header, userId, prodId, isCallback):
    initData = {}
    body = {}
    initData['userId'] = userId
    initData['merchantId'] = '1604000006'
    initData['prodId'] = prodId#'web.points.120'
    initData['paymentType'] = 1
    initData['orderDescription'] = '訂單描述'
    initData['returnURL'] = 'https://gateway-test.yipay.com.tw/demo/return'
    initData['cancelURL'] = 'https://gateway-test.yipay.com.tw/demo/cancel'
    initData['notificationEmail'] = 'lisa@truelove.dev'
    initData['receiptDonate'] = True
    initData['receiptName'] = 'QA Test'
    initData['receiptTel'] = '0988111111'
    initData['receiptAddr'] = '地球宇宙防衛廳'
    initData['receiptEmail'] = 'lisa@truelove.dev'
    initData['businessNo'] = ''
    if isCallback:
        res = api.yipay_init(prefix, initData, header)
        restext = json.loads(res.text)
        pprint(restext)
        payload = OrderedDict()
        body['merchantId'] = '1604000006'
        body['type'] = 1
        body['amount'] = restext['amount']
        body['orderNo'] = restext['orderNo']
        body['transactionNo'] = 'DD1234567'
        body['statusCode'] = '00'
        body['statusMessage'] = 'Success'
        body['approvalCode'] = 'QAR123456'
        payload['merchantId'] = '1604000006'
        payload['amount'] = str(restext['amount'])
        payload['orderNo'] = restext['orderNo']
        payload['returnURL'] = 'https://gateway-test.yipay.com.tw/demo/return'
        payload['cancelURL'] = 'https://gateway-test.yipay.com.tw/demo/cancel'
        payload['backgroundURL'] = restext['backgroundURL']
        payload['transactionNo'] = 'DD1234567'
        payload['statusCode'] = '00'
        payload['approvalCode'] = 'QAR123456'
        body['checkCode'] = yipayencode(payload)
        api.yipay_callback(prefix, body, header)
    else:
        api.yipay_init(prefix, initData, header)


def Openroom(env, head, opentime, isZego, roomId, roomtitle, sleeptime):
    try: 
        if isZego:
            print('Zego head = %s'%head)
        else:      
            print('中華 head = %s'%head)
        sockinfo = api.get_load_balance(env, head)
        sip = sockinfo['socketIp']
        sport = int(sockinfo['socketPort'])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (sip, sport)
        sock.connect(server_address)
        chatlib.chat_room_auth(sock, head)  
        if isZego:
            print('open at zego')
            rid = chatlib.enterZego(sock, roomId)
            print('Zego Open finish, room Id = %d' % rid)
        else:
            print('open at 中華')
            rid = chatlib.new_room(sock, roomtitle)
            print('中華Open finish, room Id = %d' % rid)
        start_time = time.time()
        while 1:
            print('Zego keep live') if isZego else print('China keep live') 
            time.sleep(sleeptime)
            end_time = time.time()
            if (end_time - start_time) > opentime:                
                chatlib.leave_room(rid, sock)   
                print('Zego Close Room') if isZego else print('China Close Room')        
                break
            chatlib.keep_live(sock)
        return rid
    except Exception as e:
        print(e)


def execut_calculate_statistics(hostAddr):
    keyfile = '../assistence/lisakey'  
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostAddr, username='lisa', key_filename=keyfile)
    cmd = 'cd /var/www/apiv2/; ls -la;'
    startdate = (datetime.today() - timedelta(days=datetime.today().day+2)).strftime('%Y-%m-01')  
    cmd += './venv/bin/python calculate_statistics.py ' + startdate
    #print ('command = %s' %cmd)
    #stdin, stdout, stderr = ssh.exec_command(cmd)
    ssh.exec_command(cmd)
    '''
    while not stdout.channel.exit_status_ready(): 
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [ ], [ ], 0.0)
            if len(rl) > 0:
                tmp = stdout.channel.recv(1024)
                output = tmp.decode()
                print (output)
    '''
    ssh.close()

def createAccount(env, accountPrefix, countNum):
    header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    result = api.user_login(env, 'tl-lisa', '12345678')
    header['X-Auth-Token'] = result['token']
    header['X-Auth-Nonce'] = result['nonce']            
    idlist = []
    for i in range(countNum + 1):
        account = accountPrefix + '00' + str(i)
        api.register(env, account, header)
        uid = api.search_user(env, account, header)
        api.change_user_mode(env, uid, -2, header)
        api.change_user_mode(env, uid, 1, header)
        idlist.append(uid)
    # 1:admin;4:直撥主;5:一般用戶;:liveController:10
    api.change_roles(env, header, idlist, 10)
    return
