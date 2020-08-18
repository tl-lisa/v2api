import json
import os
import time
from report import createReportData
from assistence import dbConnect
from assistence import sundry

def getData(userList, masterList, db):
    #送禮  
    actionDic = {
        2: {
            masterList[0]:{
                'funcName' :[
                    createReportData.createLiveRoom, 
                    createReportData.joinGame
                ],
                'parameter':[
                    [db, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                    [db, masterList[0], userList[0], ' 09:00:00']
                ]
            },
            masterList[1]:{
                'funcName' :[createReportData.sendPostGift, createReportData.sendPostGift, createReportData.IMPoint],
                'parameter':[[db, masterList[1] , userList[1], 893], [db, masterList[1] , userList[1], 893], [db, masterList[1] , userList[0]]]
            }
        },
        1: {
            masterList[0]:{
                'funcName' :[
                    createReportData.createLiveRoom, 
                    createReportData.joinGame,
                    createReportData.createLiveShow, 
                    createReportData.sendLiveRoomGift, 
                    createReportData.sendLiveShowGift,
                    createReportData.createLiveRoom
                ],
                'parameter':[
                    [db, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                    [db, masterList[0], userList[0], ' 09:00:00'],
                    [db, masterList[0], [' 08:00:00', ' 09:30:30']],
                    [db, masterList[0], userList[1], ' 09:05:30', '5976e63d-7166-4585-a3a3-fb48efed9a37'], 
                    [db, masterList[0], userList[0], ' 09:06:30', '3d839c5a-e4cd-419d-aaa5-d15c113dc0cc'],
                    [db, masterList[0], [[' 13:50:00', ' 14:55:00'], [' 15:00:00', ' 15:15:00']]]
                ]
            },
            masterList[1]:{
                'funcName' :[createReportData.sendPostGift, createReportData.IMPoint],
                'parameter':[[db, masterList[1] , userList[1], 893], [db, masterList[1] , userList[0]]
                ]
            },
            masterList[2]:{
                'funcName' :[createReportData.createLiveRoom],
                'parameter':[[db, masterList[2], [[' 14:10:00', ' 14:55:00'], [' 15:01:00', ' 15:55:00'], [' 16:00:00', ' 16:55:00']]]]
            },
            masterList[3]:{
                'funcName' :[createReportData.createLiveRoom],
                'parameter':[[db, masterList[3], [[' 13:50:00', ' 14:55:00'], [' 15:00:00', ' 15:15:00']]]]
            }
        },
        0: {
            masterList[0]:{
                'funcName' :[
                    createReportData.createLiveRoom, 
                    createReportData.sendLiveRoomGift, 
                    createReportData.createLiveRoom
                ],
                'parameter':[
                    [db, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                    [db, masterList[0] , userList[1], ' 09:05:30', '5976e63d-7166-4585-a3a3-fb48efed9a37'], 
                    [db, masterList[0], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:55:00'], [' 12:23:00', ' 13:33:00'], [' 14:10:00', ' 14:20:00'], [' 15:51:00', ' 15:58:00'], [' 16:01:00', ' 16:03:00']]]
                ]
            },
            masterList[1]:{
                'funcName' :[createReportData.sendPostGift, createReportData.IMPoint],
                'parameter':[[db, masterList[1] , userList[1], 894], [db, masterList[1] , userList[0]]
                ]
            },
            masterList[2]:{
                'funcName' :[createReportData.createLiveRoom],
                'parameter':[[db, masterList[2], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:11:00'], [' 11:23:00', ' 12:11:00'], [' 15:01:00', ' 15:15:00']]]]
            },
            masterList[3]:{
                'funcName' :[createReportData.createLiveRoom, createReportData.joinGame, createReportData.joinGame],
                'parameter':[
                    [db, masterList[3], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:55:00']]],
                    [db, masterList[0], userList[0], ' 10:25:00'],
                    [db, masterList[0], userList[0], ' 10:30:00']
                ]
            }
        }
    }

    if os.path.isfile('report.txt'):
        with open('report.txt') as json_file:
            result = json.load(json_file)
    else:
        createReportData.clearData(db)
        result = createReportData.createData(actionDic) 
        sqlstr  = "select i.id, i.login_id, i.nickname, u.sex, it.tag_id, ta.group_id, ag.agency_id "
        sqlstr += "from identity i left join user_settings u on i.id = u.identity_id "
        sqlstr += "left join agency_master_contract ag on i.id = ag.identity_id "
        sqlstr += "left join identity_tag_association it on i.id = it.identity_id "
        sqlstr += "left join tag_association ta on it.tag_id = ta.tag_id  where i.id in ('"
        for i in range(len(masterList)):
            sqlstr += masterList[i]
            sqlstr += "')" if len(masterList) - i == 1 else "', '"
        dbResult = dbConnect.dbQuery(db, sqlstr)
        for i in dbResult:
            if result[i[0]].get('info') == None:
                result[i[0]]['info'] = {}
            result[i[0]]['info']['userId'] = i[0]
            result[i[0]]['info']['nickname'] = i[2]
            result[i[0]]['info']['loginId'] = i[1]
            result[i[0]]['info']['gender'] = 'male' if i[3] == 1 else 'female'
            result[i[0]]['info']['tagGroups'] = i[5]
            result[i[0]]['info']['tags'] = i[4]
            result[i[0]]['info']['agencyId'] = str(i[6])
            result[i[0]]['info']['max'] = 7200 if i[5] == 1 else 10800
        with open('report.txt', 'w') as outfile:
            json.dump(result, outfile)
        sundry.execut_calculate_statistics(db)
        time.sleep(30)
    return result