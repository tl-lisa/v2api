#milestone22 補入送禮者的經驗值；順便補入相關case
import json
import requests
import pymysql
import time
import string
import pytest
from assistence import api
from assistence import initdata
from assistence import dbConnect
from assistence import liveshowLib
from pprint import pprint
from datetime import datetime, timedelta

env = 'QA'
test_parameter = {}
header = {'Content-Type': 'application/json', 'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
idList = []
memberList = []
liveshowId = []

def setup_module():
    initdata.set_test_data(env, test_parameter)
    initdata.clearLiveshowData(test_parameter['db'])
    initdata.initIdList(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], [test_parameter['broadcaster_acc'],
    test_parameter['user_acc'], test_parameter['user1_acc']], idList)
    liveshowLib.createMember(test_parameter['prefix'], test_parameter['backend_token'], test_parameter['backend_nonce'], memberList)
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']
    liveshowLib.liveshowPrepare(test_parameter['prefix'], test_parameter['db'], header, 'TrueLove teams', 2, 0, 2, 3, 351, '', 
    False, False, memberList, liveshowId) 

#scenario, token, nonce, idIndex, giftIdIndex, roomId, giver, target, team, expected (gift id = 1086 is for live_show)
testData = [
    ('happy case', 'user_token', 'user_nonce', 0, 0, 1, 1, 1, '1', True, 2),
    ('happy case', 'user_token', 'user_nonce', 0, 0, 1, 1, 4, '2', False, 2),
    ('user does not have point', 'user1_token', 'user1_nonce', 0, 0, 1, 2, 1, '1', False, 4),
    ('liveShowId is wrong', 'user_token', 'user_nonce', 2, 0, 1, 1, 1, '1', False, 4),
    ('target user is not exist', 'user_token', 'user_nonce', 0, 0, 1, 1, -1, '1', False, 2),
    ('team is not exist', 'user_token', 'user_nonce', 0, 0, 1, 1, 4, '3', False, 4)
]

class TestSend():
    remainPoints = 2000
    giftPoine = 300
    experience = 0
    byTeam = {}
    byGuest = {}
    def setup_class(self):
        sqlList = []
        sqlList.append("update remain_points set remain_points = 2000 where identity_id = '" + idList[1] + "'")
        dbConnect.dbSetting(test_parameter['db'], sqlList)
    
    def getExperience(self, idInfo):
        sqlStr = "select identity_id, experience from user_experience where identity_id in ('" 
        for i in range (len(idInfo)):
            sqlStr += idInfo[i]
            if len(idInfo) - i == 1:
                sqlStr += "')" 
            else:
                sqlStr += "', '"
        result = dbConnect.dbQuery(test_parameter['db'], sqlStr)
        pprint(result)
        return result

    @pytest.mark.parametrize('scenario, token, nonce, idIndex, giftId, roomId, giver, target, team, isDelete, expected', testData)         
    def test_sendGift(self, scenario, token, nonce, idIndex, giftId, roomId, giver, target, team, isDelete, expected):
        giftList = ['4700b45c-dc93-4807-a91f-b4c717e66f06', '04310750-994e-41d3-8b2c-62674df24db2']
        if team not in self.byTeam:
            self.byTeam[team] = 0
        header['X-Auth-Token'] = test_parameter[token]
        header['X-Auth-Nonce'] = test_parameter[nonce]
        apiName = '/api/v2/liveshow/sendGift'
        if idIndex > 0:
            liveId = '9999'
        else:
            sqlStr = "select liveshow_id from liveshow where id = " + str(liveshowId[idIndex])
            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            liveId = record[0][0]
        if roomId > 1:
            rId = 9999
        else:
            sqlStr = "select room_id from liveshow_streaming where liveshow = " + str(liveshowId[0])
            record = dbConnect.dbQuery(test_parameter['db'], sqlStr)
            rId = record[0][0]
        if target >= 0:
            targetId = memberList[target]['id']
        else:
            targetId = 'jdoaiejraeh 999skjfp'
        if targetId not in self.byTeam:
            self.byGuest[targetId] = 0
        bfExperience = self.getExperience([targetId, idList[giver]])
        body = {
            'liveshowId': liveId,
            'giftId': giftList[giftId],
            'roomId': rId,
            'giveUserId': idList[giver],
            'targetUserId': targetId,
            'teamId': team
        }
        res = api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)
        assert res.status_code // 100 == expected
        if expected == 2:
            afExperience = self.getExperience([targetId, idList[giver]])
            restext = json.loads(res.text)
            restext['remainPoints'] == self.remainPoints - self.giftPoine
            self.byTeam[team] = self.byTeam[team] + self.giftPoine
            self.byGuest[targetId] = self.byGuest[targetId] + self.giftPoine
            for i in range(2):
                if bfExperience[i][0] == targetId:
                    assert afExperience[i][1] - bfExperience[i][1] == self.giftPoine
                else:
                    assert afExperience[i][1] - bfExperience[i][1] == self.giftPoine * 3
            assert restext['points']['byTeam'][team] == self.byTeam[team]
            assert restext['points']['byGuest'][targetId] == self.byGuest[targetId]
        if isDelete:
            header['X-Auth-Token'] = test_parameter['backend_token']
            header['X-Auth-Nonce'] = test_parameter['backend_nonce']
            apiName = '/api/v2/backend/liveshow/establish/' + str(liveshowId[0])
            res = api.apiFunction(test_parameter['prefix'], header, apiName, 'delete', None)
            assert res.status_code // 100 == 4
