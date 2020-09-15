import json
import os
import time
from report import createReportData
from report import dbConnect
from assistence import sundry
from datetime import datetime, timedelta
from pprint import pprint

def getData(userList, masterList, db):
    server = dbConnect.createSSH(db)
    try:
        server.start()
        actionDic = {
            2: {
                masterList[0]:{
                    'funcName' :[
                        createReportData.createLiveRoom, 
                        createReportData.joinGame
                    ],
                    'parameter':[
                        [server, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                        [server, masterList[0], userList[0], ' 09:00:00']
                    ]
                },
                masterList[1]:{
                    'funcName' :[createReportData.sendPostGift, createReportData.sendPostGift, createReportData.IMPoint],
                    'parameter':[[server, masterList[1] , userList[1], 893], [server, masterList[1] , userList[1], 893], [server, masterList[1] , userList[0]]]
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
                        [server, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                        [server, masterList[0], userList[0], ' 09:00:00'],
                        [server, masterList[0], [' 08:00:00', ' 09:30:30']],
                        [server, masterList[0], userList[1], ' 09:05:30', '5976e63d-7166-4585-a3a3-fb48efed9a37'], 
                        [server, masterList[0], userList[0], ' 09:06:30', '3d839c5a-e4cd-419d-aaa5-d15c113dc0cc'],
                        [server, masterList[0], [[' 13:50:00', ' 14:55:00'], [' 15:00:00', ' 15:15:00']]]
                    ]
                },
                masterList[1]:{
                    'funcName' :[createReportData.sendPostGift, createReportData.IMPoint],
                    'parameter':[[server, masterList[1] , userList[1], 893], [server, masterList[1] , userList[0]]
                    ]
                },
                masterList[2]:{
                    'funcName' :[createReportData.createLiveRoom],
                    'parameter':[[server, masterList[2], [[' 14:10:00', ' 14:55:00'], [' 15:01:00', ' 15:55:00'], [' 16:00:00', ' 16:55:00']]]]
                },
                masterList[3]:{
                    'funcName' :[createReportData.createLiveRoom],
                    'parameter':[[server, masterList[3], [[' 13:50:00', ' 14:55:00'], [' 15:00:00', ' 15:15:00']]]]
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
                        [server, masterList[0], [[' 09:00:00', ' 09:30:00']]], 
                        [server, masterList[0] , userList[1], ' 09:05:30', '5976e63d-7166-4585-a3a3-fb48efed9a37'], 
                        [server, masterList[0], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:55:00'], [' 12:23:00', ' 13:33:00'], [' 14:10:00', ' 14:20:00'], [' 15:51:00', ' 15:58:00'], [' 16:01:00', ' 16:03:00']]]
                    ]
                },
                masterList[1]:{
                    'funcName' :[createReportData.sendPostGift, createReportData.IMPoint],
                    'parameter':[[server, masterList[1] , userList[1], 894], [server, masterList[1] , userList[0]]
                    ]
                },
                masterList[2]:{
                    'funcName' :[createReportData.createLiveRoom],
                    'parameter':[[server, masterList[2], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:11:00'], [' 11:23:00', ' 12:11:00'], [' 15:01:00', ' 15:15:00']]]]
                },
                masterList[3]:{
                    'funcName' :[createReportData.createLiveRoom, createReportData.joinGame, createReportData.joinGame],
                    'parameter':[
                        [server, masterList[3], [[' 10:10:00', ' 10:20:00'], [' 10:23:00', ' 11:55:00']]],
                        [server, masterList[0], userList[0], ' 10:25:00'],
                        [server, masterList[0], userList[0], ' 10:30:00']
                    ]
                }
            }
        }

        if os.path.isfile('report.txt'):
            with open('report.txt') as json_file:
                result = json.load(json_file)
        else:
            sqlList = []
            createReportData.clearData(server)
            result = createReportData.createData(actionDic) 
            sqlstr  = "select i.id, i.login_id, i.nickname, u.sex "
            sqlstr += "from identity i inner join user_settings u on i.id = u.identity_id where i.id in ('"
            midDate1 = (datetime.today() - timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
            midDate = (datetime.today() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S')
            cDate = (datetime.today() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            for i in range(len(masterList)):
                sqlstr += masterList[i]
                sqlstr += "')" if len(masterList) - i == 1 else "', '"
                sqlStr1  = "insert into agency_master_contract(create_at, contract_end_date, contract_start_date, master_charge_rate, agency_id, identity_id, version) values "
                sqlStr1 += "('" + cDate + "', '" + midDate + "', '2017-10-01 00:00:00', 0.3, " + str(i * 2 + 1) + ", '" + masterList[i] + "', 1), "
                sqlStr1 += "('" + cDate + "',  '2028-10-01 00:00:00', '" + midDate1 + "', 0.3, " + str(i * 2 + 2) + ", '" + masterList[i] + "', 2)"
                sqlList.append(sqlStr1)
            dbConnect.execSQL(server, sqlList)
            dbResult = dbConnect.execQuery(server, sqlstr)
            for i in dbResult:
                agency = {}
                tagGroups = []
                tag = []
                sqlstr  = "select ac.agency_id, a.agency_name from agency_master_contract ac, agency a where "
                sqlstr += "ac.identity_id = '" + i[0] + "' and ac.agency_id = a.id order by ac.contract_end_date desc"
                dbResult1 = dbConnect.execQuery(server, sqlstr)
                for j in range (len(dbResult1)):
                    agency[j]= {'id': dbResult1[j][0], 'name': dbResult1[j][1]}
                sqlstr  = "select it.tag_id, ta.group_id from identity_tag_association it "
                sqlstr += "inner join tag_association ta on it.tag_id = ta.tag_id  where identity_id = '" + i[0] + "'"
                dbResult1 = dbConnect.execQuery(server, sqlstr)
                if result[i[0]].get('info') == None:
                    result[i[0]]['info'] = {}
                for j in dbResult1:
                        tag.append(j[0])
                        tagGroups.append(j[1])
                result[i[0]]['info']['tagGroups'] = tagGroups
                result[i[0]]['info']['tags'] = tag
                result[i[0]]['info']['max'] = 7200 if 1 in result[i[0]]['info']['tagGroups'] else 10800
                result[i[0]]['info']['userId'] = i[0]
                result[i[0]]['info']['nickname'] = i[2]
                result[i[0]]['info']['loginId'] = i[1]
                result[i[0]]['info']['gender'] = 'male' if i[3] == 1 else 'female'
                result[i[0]]['info']['agencyInfo'] = agency
            with open('report.txt', 'w') as outfile:
                json.dump(result, outfile)
            sundry.execut_calculate_statistics(db)
            time.sleep(30)
        return result
    except Exception as err:
        print("Error %s" % (err))
    finally:         
        server.stop()        
