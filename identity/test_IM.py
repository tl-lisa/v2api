#mileston18 IM要判斷黑名單，直播主不會取到黑名單的聊天室，但user被黑仍可發訊息#757
import json
import requests
import time
import string
import pytest
from ..assistence import api
from ..assistence import initdata
from ..assistence import dbConnect
from pprint import pprint
from datetime import datetime, timedelta

env = 'testing'
test_parameter = {}
idList = []
createTime = []
header = {'Connection': 'Keep-alive', 'X-Auth-Token': '', 'X-Auth-Nonce': ''}
parameterList = ['receiver', 'origin', 'msgType', 'textContent', 'imageUrl', 'previewUrl', 'videoUrl']


def createMessage(recevier, sender, header, msgtype, content, photo_url, preview_url, video_url):
        valuesList = []
        body = {}
        apiName = '/api/v2/backend/instantMessage'
        valuesList.extend([recevier, sender, msgtype, content, photo_url, preview_url, video_url])           
        for i in range (len(valuesList)):
            body[parameterList[i]] = valuesList[i]
        api.apiFunction(test_parameter['prefix'], header, apiName, 'post', body)


def setup_module():
    initdata.set_test_data(env, test_parameter)   
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']                  
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['broadcaster1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['backend_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['liveController1_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user_acc'], header))
    idList.append(api.search_user(test_parameter['prefix'], test_parameter['user1_acc'], header))    
    initdata.resetData(test_parameter['db'], idList[0])

def teardown_module():
    print('i am teardown')
    header['X-Auth-Token'] = test_parameter['backend_token']
    header['X-Auth-Nonce'] = test_parameter['backend_nonce']   
    api.change_roles(test_parameter['prefix'], header, [idList[0]], '4') #轉回直播主


def getData(testType):
    pass

class TestgetRoomList():
    dialogIdList = []
    @pytest.mark.parametrize("scenario, isCreateMsg, isBlack, isChangeRole, sendertoken, sendernonce, receviertoken, receivernonce, expected", getData('getRoom'))
    def testGetRoom(self):
        pass
