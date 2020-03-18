import base64
import hashlib
import hmac
import json
import time
import requests
from python_settings import settings
from . import setting as mysetting

settings.configure(mysetting) 


def create_auth_url():
    from urllib.parse import urlencode
    print('call authorize')
    url = "https://access.line.me/oauth2/v2.1/authorize"
    data = {}
    data['response_type'] = 'code'
    data['client_id'] = settings.client_id
    data['redirect_uri'] = settings.callback_URL
    data['state'] = 'test'
    data['scope'] = 'openid profile'
    res =  "{}?{}".format(url, urlencode(data))
    print(res)