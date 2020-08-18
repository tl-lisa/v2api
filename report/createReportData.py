import time
import json
from assistence import api
from assistence import initdata
from assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

resultDic = {}
def checkExist(checkDic, dayDeff):
    #pprint(resultDic)
    masterBody = {
        'points':{'points':0, 'liveroomPoints':0, 'postwallPoints':0, 'imPoints':0, 'liveshowPoints':0, 'gamePoints':0},
        'onAir':{'active': 0, 'real':0, 'hot':0},
        'detail':[],
        'summary':[]
    }
    userBody = {
        'points':0,
        'detail':[]
    }
    keys = checkDic.keys()
    for i in keys:
        if resultDic.get(checkDic[i]):
            if resultDic.get(checkDic[i]).get(str(dayDeff)) == None:  
                resultDic[checkDic[i]][str(dayDeff)] = masterBody if i == 'masterBody' else userBody
            else:
                continue
        else:
            resultDic[checkDic[i]] = {str(dayDeff): masterBody} if i == 'masterBody' else {str(dayDeff): userBody}

def caculateTime(masterId, onAirList, dayDeff):
    checkExist({'masterBody':masterId}, dayDeff)
    dayStr = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d') 
    continueNum = -1
    lastContinueNum = -1
    for i in range(len(onAirList)):
        begDatetime = dayStr + onAirList[i][0]
        endDatetime = dayStr + onAirList[i][1]
        #熱力榜時間計算
        if (int(onAirList[i][0][1]) * 10 + int(onAirList[i][0][2])) < 16:
            resultDic[masterId][str(dayDeff)]['onAir']['hot'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        elif all([(int(onAirList[i][0][1]) * 10 + int(onAirList[i][0][2])) >= 16, dayDeff > 0]):
            if resultDic[masterId].get(str(dayDeff - 1)):
                resultDic[masterId][str(dayDeff - 1)]['onAir']['hot'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
            else:
                resultDic[masterId][str(dayDeff - 1)] = {
                    'points':{'points':0, 'liveroomPoints':0, 'postwallPoints':0, 'imPoints':0, 'liveshowPoints':0, 'gamePoints':0},
                    'onAir':{'active': 0, 'real':0, 'hot':0},
                    'detail':[],
                    'summary':[]
                }
                resultDic[masterId][str(dayDeff - 1)]['onAir']['hot'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        if all([(len(onAirList) - i > 1), i > continueNum]):
            for j in range(i + 1, len(onAirList)):
                begDatetime1 = dayStr + onAirList[j][0]
                endDatetime1 = dayStr + onAirList[j][1]
                if int((datetime.strptime(begDatetime1, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) <= 300:
                    endDatetime = endDatetime1
                    currentContinueNum = j
                else: 
                    break
        if any([
                all([resultDic[masterId][str(dayDeff)]['onAir']['active'] > 0, i > lastContinueNum]),
                all([resultDic[masterId][str(dayDeff)]['onAir']['active'] == 0,
                int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) >= 3600])
            ]):
            lastContinueNum = currentContinueNum
            resultDic[masterId][str(dayDeff)]['onAir']['active'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
            resultDic[masterId][str(dayDeff)]['onAir']['real'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))
        elif resultDic[masterId][str(dayDeff)]['onAir']['active'] == 0:
            resultDic[masterId][str(dayDeff)]['onAir']['real'] += int((datetime.strptime(endDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s')) - int((datetime.strptime(begDatetime, "%Y-%m-%d %H:%M:%S")).strftime('%s'))

def updateResult(db, masterId, userId, dayDeff, giftName, pointKind, point, createAt, category, gId):
    checkExist({'masterBody': masterId, 'userBody': userId}, dayDeff)
    if pointKind != 'liveroomPoints':
        res = dbConnect.dbQuery(db, "select max(id) from point_consumption_history")
    mGiftDic = {'name': giftName, 'points': point, 'create_at': int((datetime.strptime(createAt, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s')), 'uid': userId, 'giftId': gId, 'historyId': None}
    uGiftDic = {'name': giftName, 'points': point, 'create_at': int((datetime.strptime(createAt, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%s')), 
                'liveMasterId': masterId, 'giftCategory': category, 'giftId': gId, 'historyId': res[0][0] if pointKind != 'liveroomPoints' else 0}
    resultDic[masterId][str(dayDeff)]['points']['points'] += point
    resultDic[masterId][str(dayDeff)]['points'][pointKind] += point
    resultDic[masterId][str(dayDeff)]['detail'].insert(0, mGiftDic)
    resultDic[userId][str(dayDeff)]['detail'].insert(0, uGiftDic)
    resultDic[userId][str(dayDeff)]['points'] += point
    isNotFound = True
    if len(resultDic[masterId][str(dayDeff)]['summary']) > 0:  
        for j in resultDic[masterId][str(dayDeff)]['summary']:
            if j.get(userId):
                j[userId] += point
                isNotFound = False
                break
    if any([len(resultDic[masterId][str(dayDeff)]['summary']) == 0, isNotFound]):
        resultDic[masterId][str(dayDeff)]['summary'].append({userId: point})

def createLiveRoom(db, masterId, timeList, dayDeff):
    sqlList = []
    dayStr = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d') 
    for i in timeList:
        begDatetime = dayStr + i[0]
        endDatetime = dayStr + i[1]
        sqlStr = "insert into live_room set chat_server_id = 412, title = 'test', current_count = 0, total_count = 1, total_users = 1, status = 0, "
        sqlStr += "live_master_id = '" + masterId + "', "
        sqlStr += "create_at = '" + begDatetime + "', "
        sqlStr += "end_at = '" + endDatetime + "'"
        sqlList.append(sqlStr)
    dbConnect.dbSetting(db, sqlList)
    caculateTime(masterId, timeList, dayDeff)

def createLiveShow(db, masterId, timeList, dayDeff):
    sqlList = []
    dayStr = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d')
    begDatetime = dayStr + timeList[0]
    endDatetime = dayStr + timeList[1]
    sqlStr = "insert into liveshow set liveshow_id = '" + 'qa_test' + str(dayDeff) + "', " 
    sqlStr += "title = 'qa_test', liveshow_type = 'individual', gift_category = 127, "
    sqlStr += "pool_id = '"    + masterId + "', "
    sqlStr += "start_time = '" +  begDatetime   + "', "
    sqlStr += "end_time = '"   +  endDatetime   + "', "
    sqlStr += "create_at = '"  +  begDatetime   + "', "
    sqlStr += "update_at = '"  +  begDatetime   + "'"
    sqlList.append(sqlStr)
    sqlStr = "insert into liveshow_team set  team_id = 'test1', name = 'QA test', "
    sqlStr += "liveshow = (select max(id) from liveshow), "
    sqlStr += "create_at = '" +  begDatetime + "', "
    sqlStr += "update_at = '" +  begDatetime  + "'"
    sqlList.append(sqlStr)
    dbConnect.dbSetting(db, sqlList)

def createPhotoPost(db, masterId, dayDeff):
    dayStr = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into photo_post set version = 0, type = 'photo', "
    sqlStr += "photo_path = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png', "
    sqlStr += "photo_thumb_path = 'https://d3eq1e23ftm9f0.cloudfront.net/story/photo/6e7103c048cd11ea83b942010a8c0017.png', "
    sqlStr += "create_user_id = '" + masterId + "', "
    sqlStr += "update_user_id = '" + masterId + "', "
    sqlStr += "owner_id = '"       + masterId + "', "
    sqlStr += "create_at = '"      + dayStr   + "', "
    sqlStr += "update_at = '"      + dayStr   + "'"
    dbConnect.dbSetting(db, [sqlStr])

def createRemainPointHistory(db, userId, point, reason, dayDeff):
    dayStr = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into point_remain_points_historyconsumption_history set ratio = 3.44, addratio = 3.44, version = 0, "
    sqlStr += "create_at = '"       + dayStr    + "', "
    sqlStr += "update_at = '"       + dayStr    + "', "
    sqlStr += "create_user_id = '"  + userId    + "', "
    sqlStr += "update_user_id = '"  + userId    + "', "
    sqlStr += "identity_id = '"     + userId    + "', "
    sqlStr += "reason = '"          + reason    + "', "
    sqlStr += "remain_points = 500," 
    sqlStr += "add_points = "       + str(0 - point) 
    dbConnect.dbSetting(db, [sqlStr])

def addPointConsumptionHistory(db, gift_type, sender_id, receiver_id, point, dayDeff):
    dayStr = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into point_consumption_history set ratio = 3.44, "
    sqlStr += "gift_type = '"   + gift_type     + "', "
    sqlStr += "sender_id = '"   + sender_id     + "', "
    sqlStr += "receiver_id = '" + receiver_id   + "', "
    sqlStr += "point = "        + str(point)    +  ", "
    sqlStr += "create_at = '"   + dayStr        + "'"
    dbConnect.dbSetting(db, [sqlStr])

def createGameRoom(db):
    sqlStr = "select id, create_at from live_room order by id desc limit 1"
    result = dbConnect.dbQuery(db, sqlStr)
    sqlStr  = "insert into game_room set game_category_id = 2, "
    sqlStr += "live_room_id = " + str(result[0][0]) + ", "
    sqlStr += "created_at = '"  + str(result[0][1]) + "', "
    sqlStr += "updated_at = '"  + str(result[0][1]) + "' "
    dbConnect.dbSetting(db, [sqlStr])

def createIM(db, senderId, receiverId, dayDeff):
    dayStr = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    dialogId = 'f1d34ca04158d16028cb82b85b4c7db49dcc22cffb2f07186594486d4789d21d'
    sqlStr  = "insert into instant_message set msg_type = 'text', "
    sqlStr += "dialog_id = '"   + dialogId      + "', "
    sqlStr += "receiver_id = '" + receiverId    + "', "
    sqlStr += "sender_id = '"   + senderId      + "', "
    sqlStr += "create_at = '"   + dayStr        + "'"
    dbConnect.dbSetting(db, [sqlStr])

def getNameAndPoint(db, condition):
    sqlStr = "select name, point, category_id from gift_v2 where " + condition
    result = dbConnect.dbQuery(db, sqlStr)
    return result[0][0], result[0][1], result[0][2]

def sendLiveShowGift(db, masterId, userId, timeStr, uuid, dayDeff): #liveshow禮物
    giftName, giftPoint, category = getNameAndPoint(db, "uuid = '" + uuid + "'")
    dayStr = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d')
    createAt = (datetime.strptime(dayStr + timeStr, '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%d %H:%M:%S')
    addPointConsumptionHistory(db, 'liveshow', userId, masterId, giftPoint, dayDeff)
    sqlStr  = "insert into liveshow_gift_history set ratio = 3.33, "
    sqlStr += "points = " + str(giftPoint) + ", "
    sqlStr += "liveshow=(select max(id) from liveshow), "
    sqlStr += "team=(select max(id) from liveshow_team), "
    sqlStr += "room_id=(select max(id) from live_room), "
    sqlStr += "gift_id='"           + uuid          + "', "
    sqlStr += "giver_user_id = '"   + userId        + "', "
    sqlStr += "live_master_id = '"  + masterId      + "', "
    sqlStr += "create_at = '"       + createAt       + "'"
    dbConnect.dbSetting(db, [sqlStr])
    updateResult(db, masterId, userId, dayDeff, giftName, 'liveshowPoints', giftPoint, createAt, str(category), uuid)

def sendLiveRoomGift(db, masterId, userId, timeStr, uuid, dayDeff): #直播間禮物，彈幕 目前尚未寫入PointConsumptionHistory
    sqlList = []
    giftName, giftPoint, category = getNameAndPoint(db, "uuid = '" + uuid + "'")
    dayStr = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d')
    createAt = (datetime.strptime(dayStr + timeStr, '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into live_room_gift set consumption_point = " + str(giftPoint) + ", "
    sqlStr += "room_id=(select max(id) from live_room), "
    sqlStr += "gift_id='"           + uuid          + "', "
    sqlStr += "create_user_id = '"  + userId        + "', "
    sqlStr += "target_user_id = '"  + masterId      + "', "
    sqlStr += "create_at = '"       + createAt       + "'"
    sqlList.append(sqlStr)
    updateResult(db, masterId, userId, dayDeff, giftName, 'liveroomPoints', giftPoint, createAt, category, uuid)
    barragePoint = '35' if (dayDeff % 2) == 0 else '350'
    createAt = (datetime.strptime(dayStr + timeStr, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into live_room_gift set "
    sqlStr += "consumption_point = " + barragePoint + ", "
    sqlStr += "room_id=(select max(id) from live_room), "
    sqlStr += "barrage_id='"        + str(dayDeff % 2 + 1)    + "', "
    sqlStr += "create_user_id = '"  + userId        + "', "
    sqlStr += "target_user_id = '"  + masterId      + "', "
    sqlStr += "create_at = '"       + createAt      + "'"
    sqlList.append(sqlStr)
    dbConnect.dbSetting(db, sqlList)
    updateResult(db, masterId, userId, dayDeff, '彈幕消費', 'liveroomPoints', int(barragePoint), createAt, None, '')

def joinGame(db, masterId, userId, timeStr, dayDeff):
    createGameRoom(db)
    createAt = (datetime.today() - timedelta(days=dayDeff)).strftime('%Y-%m-%d %H:%M:%S')
    addPointConsumptionHistory(db, 'game', userId, masterId, 500, dayDeff)
    sqlStr  = "insert into game_point_history set "
    sqlStr += "id=(select max(id) from point_consumption_history), "
    sqlStr += "game_room_id=(select max(id) from game_room), "
    sqlStr += "room_id=(select max(id) from live_room) "
    dbConnect.dbSetting(db, [sqlStr])
    updateResult(db, masterId, userId, dayDeff, '遊戲消費', 'gamePoints', 500, createAt, None, '')

def IMPoint(db, masterId, userId, dayDeff):
    createIM(db, userId, masterId, dayDeff)
    addPointConsumptionHistory(db, 'im_point', userId, masterId, 20, dayDeff)
    createAt = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into instant_message_point_history set "
    sqlStr += "id=(select max(id) from point_consumption_history), "
    sqlStr += "message_id=(select max(id) from instant_message) "
    dbConnect.dbSetting(db, [sqlStr])
    updateResult(db, masterId, userId, dayDeff, '私訊消費', 'imPoints', 20, createAt, None, '')

def sendPostGift(db, masterId, userId, gid, dayDeff):
    createPhotoPost(db, masterId, dayDeff)
    giftName, giftPoint, category = getNameAndPoint(db, "id = " + str(gid) )
    addPointConsumptionHistory(db, 'post_wall', userId, masterId, giftPoint, dayDeff)
    createAt = (datetime.today() - timedelta(days=dayDeff) - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    sqlStr  = "insert into post_gift_history set "
    sqlStr += "id=(select max(id) from point_consumption_history), "
    sqlStr += "post_id=(select max(id) from photo_post), "
    sqlStr += "gift_id= " + str(gid)
    dbConnect.dbSetting(db, [sqlStr])
    updateResult(db, masterId, userId, dayDeff, giftName, 'postwallPoints', giftPoint, createAt, category, gid)

def clearData(db):
    sqlList = [] 
    truncateList = ['post_gift_history', 'live_room_gift', 'liveshow_gift_history', 'game_point_history', 'instant_message_point_history', 
                    'instant_message_text', 'photo_comment', 'photo_like', 'liveshow_guest', 'live_banner_v2', 'liveshow_streaming', 'live_master_statistics']
    deleteList = ['point_consumption_history', 'photo_post', 'game_room', 'instant_message', 'liveshow_team', 'liveshow', 'live_room']
    for i in truncateList:
        sqlList.append("TRUNCATE TABLE " + i) 
    for tableName in deleteList:
        sqlList.append("delete from " + tableName)
        sqlList.append("alter table " + tableName + " auto_increment = 1")
    dbConnect.dbSetting(db, sqlList)

def createData(dataDic):
    keys1 = dataDic.keys()
    for i in keys1:
        keys2 = dataDic[i].keys()
        for j in keys2:
            for k in range(len(dataDic[i][j]['funcName'])):
                dataDic[i][j]['funcName'][k](*dataDic[i][j]['parameter'][k], i)
    return resultDic