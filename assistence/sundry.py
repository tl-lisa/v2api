import time
import socket
import paramiko
from pprint import pprint
from datetime import datetime, timedelta
from . import chatlib
from . import api

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
