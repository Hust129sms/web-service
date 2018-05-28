from app import celery
from time import sleep
import os

import httplib2
import urllib.parse

#服务地址
sms_host = "sms.yunpian.com"
voice_host = "voice.yunpian.com"
#端口号
port = 443
#版本号
version = "v2"

#模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_single_send.json"


def tpl_send_sms(apikey, tpl_id, tpl_value, mobile):
    """
    模板接口发短信
    """
    params = urllib.parse.urlencode({
        'apikey': apikey,
        'tpl_id': tpl_id,
        'tpl_value': urllib.parse.urlencode(tpl_value),
        'mobile': mobile
    })
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "charset": "utf-8",
    }
    conn = httplib2.HTTPSConnectionWithTimeout(sms_host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str


@celery.task
def send_verify_code(tel, key, id, **kwargs):
    tpl_value = dict()
    for keys in kwargs:
        tpl_value['#%s#' % keys] = kwargs[keys]
    print(tpl_send_sms(key, id, tpl_value, tel).decode())
    print(tel)
