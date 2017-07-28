#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time
import urllib
import urllib.parse
import urllib.request

import requests

import accountConfig

# 在此输入您的Key
KEY_INDEX = "CNY_1"  # 默认的key_index

ACCOUNT_INFO = "get_account_info"
GET_ORDERS = "get_orders"
ORDER_INFO = "order_info"
BUY = "buy"
BUY_MARKET = "buy_market"
CANCEL_ORDER = "cancel_order"
NEW_DEAL_ORDERS = "get_new_deal_orders"
ORDER_ID_BY_TRADE_ID = "get_order_id_by_trade_id"
SELL = "sell"
SELL_MARKET = "sell_market"

'''
发送信息到api
'''


def send2api(pParams, extra, key_index=KEY_INDEX):
    ACCESS_KEY = accountConfig.HUOBI[key_index]["ACCESS_KEY"]
    pParams['access_key'] = ACCESS_KEY
    pParams['created'] = int(time.time())
    pParams['sign'] = createSign(pParams, key_index)
    if (extra):
        for k in extra:
            v = extra.get(k)
            if (v != None):
                pParams[k] = v
                # pParams.update(extra)
    SERVICE_API = accountConfig.HUOBI[KEY_INDEX]["SERVICE_API"]
    return httpRequest(SERVICE_API, pParams)


'''
生成签名
'''


def createSign(params, key_index=KEY_INDEX):
    SECRET_KEY = accountConfig.HUOBI[key_index]["SECRET_KEY"]
    params['secret_key'] = SECRET_KEY
    params = sorted(params.items(), key=lambda d: d[0], reverse=False)
    message = urllib.parse.urlencode(params)
    message = message.encode(encoding='UTF8')
    m = hashlib.md5()
    m.update(message)
    m.digest()
    sig = m.hexdigest()
    return sig


'''
request
'''


def httpRequest(url, params):
    '''
    postdata = urllib.parse.urlencode(params)
    postdata = postdata.encode('utf-8')

    fp = urllib.request.urlopen(url, postdata, timeout = 5)
    if fp.status != 200:
        return None
    else:
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        return mystr
    '''
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }

    postdata = urllib.parse.urlencode(params)
    # postdata = postdata.encode('utf-8')
    response = requests.post(url, postdata, headers=headers, timeout=5)
    time.sleep(0.2)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpPost failed, detail is:%s" % response.text)
