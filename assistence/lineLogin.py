import base64
import hashlib
import hmac
import json
import time
import requests
from python_settings import settings
from ..assistence import setting as mysetting
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


settings.configure(mysetting) 


def create_auth_url():
    from urllib.parse import urlencode
    url = "https://access.line.me/oauth2/v2.1/authorize"
    data = {}
    data['response_type'] = 'code'
    data['client_id'] = settings.client_id
    data['redirect_uri'] = settings.callback_URL
    data['state'] = 'test'
    data['scope'] = 'openid profile'
    res =  "{}?{}".format(url, urlencode(data))
    #print(res)
    return res

def get_toke(auth_code):
    url = 'https://api.line.me/oauth2/v2.1/token'
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': settings.callback_URL,
            'client_id': settings.client_id,
            'client_secret': settings.client_secret}
    #print(body)
    res = requests.post(url, headers=header, data=body)
    print(json.loads(res.text))
    return json.loads(res.text)

def line_login():
    Browser = webdriver.Chrome()
    Browser.get(create_auth_url())
    Browser.find_element_by_name('tid').send_keys(settings.lineId)
    Browser.find_element_by_name('tpasswd').send_keys(settings.linePasswd)
    Browser.find_element_by_class_name('MdBtn01').click()
    time.sleep(1)
    code_url = Browser.current_url
    auth_code = code_url[code_url.find('=') + 1 :code_url.find('&')]
    Browser.quit()
    return (get_toke(auth_code))

def getGamil():
    import imaplib
    mailserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mailserver.login(settings.email, settings.email_password)
    status, count = mailserver.select('Inbox')
    status, data = mailserver.fetch(count[0], '(UID BODY[TEXT])')
    print (data[0][1])
    mailserver.close()
    mailserver.logout()