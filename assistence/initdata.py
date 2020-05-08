import json
import time
import sys
from . import api
from . import dbConnect

sys.dont_write_bytecode = True


def set_test_data(env, test_parameter):    
    if env == 'QA':
        #test_parameter['prefix'] = 'http://testing-api.truelovelive.com.tw'
        test_parameter['prefix'] = 'http://35.234.6.138'
        test_parameter['db'] = '35.234.6.138'
    test_parameter['user_acc'] = 'track0050'
    test_parameter['user1_acc'] = 'track0040'
    test_parameter['backend_acc'] = 'tl-lisa'
    test_parameter['broadcaster_acc'] = 'broadcaster005'
    test_parameter['broadcaster1_acc'] = 'broadcaster006'
    test_parameter['broadcaster2_acc'] = 'broadcaster007'        
    test_parameter['liveController1_acc'] = 'lv000'
    test_parameter['liveController2_acc'] = 'lv001'
    test_parameter['liveController3_acc'] = 'lv002'
    test_parameter['push_token'] = '256bdf47f4a1e956f8d6945f6fec7ab3'
    test_parameter['user_pass'] = '123456'
    test_parameter['backend_pass'] = '123456'
    test_parameter['broadcaster_pass'] = '123456'
    test_parameter['broadcaster1_pass'] = '123456'
    result = api.user_login(test_parameter['prefix'], test_parameter['user_acc'], test_parameter['user_pass'])
    test_parameter['user_token'] = result['token']
    test_parameter['user_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['liveController1_acc'], test_parameter['user_pass'])
    test_parameter['liveController1_token'] = result['token']
    test_parameter['liveController1_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['liveController2_acc'], test_parameter['user_pass'])
    test_parameter['liveController2_token'] = result['token']
    test_parameter['liveController2_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['liveController3_acc'], test_parameter['user_pass'])
    test_parameter['liveController3_token'] = result['token']
    test_parameter['liveController3_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['user1_acc'], test_parameter['user_pass'])
    test_parameter['user1_token'] = result['token']
    test_parameter['user1_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['backend_acc'], test_parameter['backend_pass'])
    test_parameter['backend_token'] = result['token']
    test_parameter['backend_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['broadcaster_acc'], test_parameter['broadcaster_pass'])
    test_parameter['broadcaster_token'] = result['token']
    test_parameter['broadcaster_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['broadcaster1_acc'], test_parameter['broadcaster1_pass'])
    test_parameter['broadcaster1_token'] = result['token']
    test_parameter['broadcaster1_nonce'] = result['nonce']
    result = api.user_login(test_parameter['prefix'], test_parameter['broadcaster2_acc'], test_parameter['broadcaster1_pass'])
    test_parameter['broadcaster2_token'] = result['token']
    test_parameter['broadcaster2_nonce'] = result['nonce']        
    test_parameter['one_time_1'] = int(time.time()) - 5
    test_parameter['err_token'] = 'aa24385'
    test_parameter['err_nonce'] = 'nceoiw'
    test_parameter['gift_id'] = 'b0a2945a-8d2b-4f5d-924a-7dd8d3a4be6b'
    test_parameter['cs_acc'] = 'qa-cs'
    result = api.user_login(test_parameter['prefix'], test_parameter['cs_acc'], '123456')
    test_parameter['cs_token'] = result['token']
    test_parameter['cs_nonce'] = result['nonce']        
    test_parameter['project_acc'] = 'qa-project'
    result = api.user_login(test_parameter['prefix'], test_parameter['project_acc'], '123456')
    test_parameter['project_token'] = result['token']
    test_parameter['project_nonce'] = result['nonce']        
    test_parameter['market_acc'] = 'qa-market'
    result = api.user_login(test_parameter['prefix'], test_parameter['market_acc'], '123456')
    test_parameter['market_token'] = result['token']
    test_parameter['market_nonce'] = result['nonce']       
    test_parameter['photo_url'] = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png'
    test_parameter['preview_url'] = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/5abd6f60deb711e9a49e42010a8c1fc8.jpg'
    test_parameter['video_url'] = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/5abd6f60deb711e9a49e42010a8c9fc8.jpg'
    test_parameter['photo1_url'] = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/537c11b848cd11ea83b942010a8c0017.png'
    header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
    changelist = [] 
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce'] 
    changelist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    changelist.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    api.change_roles(test_parameter['prefix'], header, changelist, '4') #轉回直播主
    return

def initIdList(prefix, token, nonce, accountList, idList):
    header  = {}
    header['X-Auth-Token'] = token
    header['X-Auth-Nonce'] = nonce
    for i in accountList:
        idList.append(api.search_user(prefix, i, header))
    return 
    
def clearOrder(db):
    sqlList = []
    tableList = ['remain_points_history', 'purchase_order']
    for i in tableList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr) 
    dbConnect.dbSetting(db, sqlList)


def clearIdentityData(dbInfo):
    sqlList = []
    tableList = ['identity_email_register_history', 'identity_email_bind_history', 'identity_third_party', 'identity_line', 'identity_profile']
    sqlStr = "select identity_id from identity_third_party union select identity_id from identity_profile"
    result = dbConnect.dbQuery(dbInfo, sqlStr)
    for i in tableList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)       
    delList = ['identity_role', 'remain_points', 'user_settings', 'user_experience', 'announcement_v2_identity_association', 'identity']
    for k in delList:
        for i in range(len(result)):
            for j in range(len(result[i])):
                if j == 0:
                    if k == 'identity':
                        sqlStr = "delete from " + k + " where id in ('"
                    elif k == 'announcement_v2_identity_association':
                        sqlStr = "delete from " + k + " where receiver in ('"
                    else:
                        sqlStr = "delete from " + k + " where identity_id in ('"
                sqlStr += result[i][j] 
                if len(result[i]) - j == 1:
                    sqlStr += "')"
                else:
                    sqlStr += "', '"
            sqlList.append(sqlStr)
    sqlList.append("alter table " + tableList[0] + " auto_increment = 1") 
    dbConnect.dbSetting(dbInfo, sqlList)

def clearFansInfo(db):
    sqlList = []       
    truncateList = ['user_follows', 'fans', 'user_blocks', 'fans_history', 'photo_report', 'photo_comment', 'photo_like', 'notification_v2_identity_association', 'zego_master']
    for i in truncateList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)
    sqlList.append('delete from notification_v2')
    sqlList.append('delete from photo_post')
    dbConnect.dbSetting(db, sqlList)    

def clearIMInfo(db):
    sqlList = []
    truncateList = ['instant_message_point_history', 'instant_message_video', 'instant_message_image', 'instant_message_text', 'zego_master']
    for i in truncateList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)
    deleteList = ['instant_message', 'dialog_member', 'dialog', 'quota_log', 'point_consumption_history']
    for tableName in deleteList:
        sqlStr = 'delete from ' + tableName
        sqlList.append(sqlStr)       
    for tableName in deleteList:
        sqlList.append("alter table " + tableName + " auto_increment = 1")
    dbConnect.dbSetting(db, sqlList)
    

def clearPhoto(db):
    sqlList = []
    truncateList = ['post_gift_history', 'photo_report', 'photo_comment', 'photo_like']
    for i in truncateList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)
    deleteList = ['quota_log', 'post_gift_history', 'point_consumption_history', 'photo_post']
    for tableName in deleteList:
        sqlStr = 'delete from ' + tableName
        sqlList.append(sqlStr)       
    for tableName in deleteList:
        sqlList.append("alter table " + tableName + " auto_increment = 1")
    dbConnect.dbSetting(db, sqlList)


def resetData(dbenv, live_master_id):
    sqlList = []
    sqlList.append("update gift_v2 set deleted_at = NULL, is_active = 1")
    sqlList.append("update gift_category_v2 set deleted_at = NULL, start_time = NULL, end_time = NULL")
    truncateList = ['user_follows', 'fans', 'user_blocks', 'fans_history', 'instant_message_point_history', 'instant_message_video', 'instant_message_image', 'instant_message_text', 'post_gift_history', 'photo_report', 'photo_comment', 'photo_like']
    truncateList.extend(['live_room_gift', 'liveshow_gift_history', 'zego_master', 'play_event_log', 'live_master_statistics', 'live_room_log', 'top_sort'])
    for i in truncateList:
        sqlStr = "TRUNCATE TABLE " + i
        sqlList.append(sqlStr)
    deleteList = ['instant_message', 'dialog_member', 'dialog', 'quota_log', 'photo_post', 'point_consumption_history', 'liveshow_team', 'live_room', 'liveshow']
    for tableName in deleteList:
        sqlStr = 'delete from ' + tableName
        sqlList.append(sqlStr)       
    for tableName in deleteList:
        sqlList.append("alter table " + tableName + " auto_increment = 1")
    dbConnect.dbSetting(dbenv, sqlList)
    
