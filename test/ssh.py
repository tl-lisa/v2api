import paramiko
import select
import time
from assistence import api
from pprint import pprint
from datetime import datetime, timedelta

def execut_calculate_statistics(hostAddr):   
    keyfile = './lisakey'  
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostAddr, username='lisa', key_filename=keyfile)
    cmd = 'cd /var/www/apiv2/; ls -la;'
    currentdate =  datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-01')  
    cmd += './venv/bin/python calculate_statistics.py ' + currentdate
    #print ('command = %s' %cmd)
    ssh.exec_command(cmd)
    '''
    stdin, stdout, stderr = ssh.exec_command(cmd)
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
yesterday = {'playTime': 0, 'points': 0}
thismonth = {'playTime': 0, 'points': 0}
lastmonth = {'playTime': 0, 'points': 0}

def dictest(dictype):
    if dictype == yesterday:
        dictype['points'] += 1 * 10
    elif dictype == thismonth:
        dictype['points'] += 1 * 20
    else:
        dictype['points'] += 1 * 30


if __name__ == '__main__':
    now = int(time.mktime((datetime.today() - timedelta(days=1)).timetuple()))
    #now = datetime.fromtimestamp(int(time.time()))# .strftime('%Y-%m-%d %H:%M:%S')
    yesterday = datetime.fromtimestamp(int(time.time())) - timedelta(days=1)
    print(now, yesterday) 
    dtDay = (datetime.today() - timedelta(days=7+datetime.today().weekday()) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    dtDay = datetime.today() - timedelta(days=1+datetime.today().weekday())
    dtDay = datetime.today().day
    dtDay = datetime.strptime('2019-12-31 00:00:00', '%Y-%m-%d %H:%M:%S')
    #print(dtDay.month)

    #pprint(yesterday)
    #pprint(thismonth)
    #pprint(lastmonth)

    testdic = {'lisa': ['1', '2', '3']}
    #print(testdic['lisa'][0])
    testdic['lisa'].pop(0)
    #print(testdic)
    #execut_calculate_statistics('testing-api.truelovelive.com.tw')
    testday = int(datetime.strptime(((datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d 16:00:00')), '%Y-%m-%d %H:%M:%S').strftime('%s'))
    #print(testday)
    
    '''
    numinfo = {}
    dicodd = {}
    diceven = {}
    odd = []
    even = []
    numtype = ['odd', 'even']
    numbername = '0-9'
    finallist = []
    for i in range(10):
        if i % 2 == 0:
            even.append(i)
        else:
            odd.append(i)
    dicodd.update({numtype[0]: odd})
    diceven.update({numtype[1]: even})
    finallist.extend([dicodd, diceven])
    numinfo.update({numbername: finallist})
    
    pprint(numinfo)

    '''

    print('lenth=%d'%(len('💞')))
    teams = {}
    for i in range(3):
        temp = {}
        temp['members'] = i
        temp['name'] = 'test'+str(i)
        teams[str(i + 1)] = temp
    pprint(teams) 
