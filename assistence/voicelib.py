import json
import time
from pprint import pprint
eventDic = {
    'phx_leave': 'voiceroom_left_bcst',
    'phx_join': 'voiceroom_in_bcst'
}


def wsConnect(ws, serverInfo, token, nonce):
    wsInfo = 'ws://' + serverInfo + '/socket/websocket?token='+token+'&nonce='+nonce
    print(wsInfo)
    ws.connect(wsInfo)
    return

def cechkEvent(ws, event):
    while 1:
        data = ws.recv()
        print('收到的回應： ' + data)
        receive_data = json.loads(data) if len(data) > 0 else None
        if receive_data['event'] == event:
            break
    return(receive_data)

def voiceOperator(ws, ref, topic, event, payload):
    body ={
        "ref": ref,
        "join_ref": ref,
        "topic": topic, 
        "event": event, 
        "payload": payload
    }
    pprint(body)
    ws.send(json.dumps(body))
    receive = cechkEvent(ws, eventDic[event]) if event == 'phx_join' else None
    pprint(receive)
    return receive