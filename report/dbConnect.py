import pymysql
import os
import time
from sshtunnel import SSHTunnelForwarder
from pprint import pprint

def createSSH(hostAddr):
    ssh_host = hostAddr #'35.201.246.119'            #SSH服务器地址
    ssh_port = 22                  #SSH端口
    keyfile = '../assistence/lisakey'            #SSH密钥
    ssh_user = 'lisa'              #SSH用户名
    db_host = '127.0.0.1'          #数据库地址
    db_port = 3306                 #数据库端口
    server = SSHTunnelForwarder(
            (ssh_host, ssh_port),            
            ssh_pkey=keyfile,
            ssh_username=ssh_user,
            remote_bind_address=(db_host, db_port))
    return server

def execQuery(server, sqlStr):
    db_host = '127.0.0.1'          #数据库地址
    db_name = 'live_casting'       #数据库名
    db_user = 'root'               #数据库用户名
    db_passwd = 'mysql'            #数据库密码
    db = pymysql.connect(
        host=db_host,
        port=server.local_bind_port,
        user=db_user,
        passwd=db_passwd,
        db=db_name,
        charset="utf8")
    cursor = db.cursor()
    collect = []
    try:    
        #print(sqlStr)
        cursor.execute(sqlStr)
        data = cursor.fetchall()
        for result in data:
            collect.append(result)
        #print(collect)
    except Exception as err:
        print("Error %s from exceute sql: %s" % (err, sqlStr))
    finally:                 
        cursor.close()
        db.close() 
    return collect

def execSQL(server, sqlList):
    db_host = '127.0.0.1'          #数据库地址
    db_name = 'live_casting'       #数据库名
    db_user = 'root'               #数据库用户名
    db_passwd = 'mysql'            #数据库密码
    db = pymysql.connect(
        host=db_host,
        port=server.local_bind_port,
        user=db_user,
        passwd=db_passwd,
        db=db_name,
        charset="utf8")
    cursor = db.cursor()
    try:    
        for i in sqlList:       
            #print(i)          
            cursor.execute(i)
        db.commit()            
    except Exception as err:
        print("Error %s from exceute sql: %s" % (err, i))
        db.rollback()       
    finally:                 
        cursor.close()
        db.close() 
    return 
