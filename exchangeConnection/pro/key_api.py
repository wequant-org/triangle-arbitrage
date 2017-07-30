#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
import time

import accountConfig


# MARKET_URL = "http://dawn-notification-peer-pro.dev-21.huobiapps.com"
MARKET_URL = "http://api.huobi.pro"
# BROKER_URL = "http://dawn-broker-pro.dev-21.huobiapps.com"
BROKER_URL = "http://api.huobi.pro"

def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-agent': 'Mozilla 5.10'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=10)
    time.sleep(0.2)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpGet failed, detail is:%s" % response.text)


def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        'User-agent': 'Mozilla 5.10'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=10)
    time.sleep(0.2)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpPost failed, detail is:%s" % response.text)


def api_key_get(params, request_path, key_index="CNY_1"):
    method = 'GET'
    ACCESS_KEY = accountConfig.PRO[key_index]["ACCESS_KEY"]
    SECRET_KEY = accountConfig.PRO[key_index]["SECRET_KEY"]
    params['AccessKeyId'] = ACCESS_KEY
    params['SignatureMethod'] = 'HmacSHA256'
    params['SignatureVersion'] = '2'
    params['Timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    host_url = BROKER_URL
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()
    params['Signature'] = createSign(params, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path
    return http_get_request(url, params)


def api_key_post(params, request_path, key_index='CNY_1'):
    method = 'POST'
    ACCESS_KEY = accountConfig.PRO[key_index]["ACCESS_KEY"]
    SECRET_KEY = accountConfig.PRO[key_index]["SECRET_KEY"]
    params_to_sign = dict()
    params_to_sign['AccessKeyId'] = ACCESS_KEY
    params_to_sign['SignatureMethod'] = 'HmacSHA256'
    params_to_sign['SignatureVersion'] = '2'
    params_to_sign['Timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    host_url = BROKER_URL
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()
    params_to_sign['Signature'] = createSign(params_to_sign, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
    return http_post_request(url, params)


def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature

'''
Market data API
'''


def get_kline(symbol, period, pick=None, long_polling=None):
    """
    :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
    :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
    :param pick: 数组形式的string，如： '["high", "low", "open", "close"]'
    :param long_polling: 可选值： { true, false }
    :return:
    """
    params = dict()
    params['symbol'] = symbol
    params['period'] = period
    if pick:
        params['pick'] = pick
    if long_polling:
        params['long-polling'] = long_polling
    url = MARKET_URL + '/market/kline'
    return http_get_request(url, params)


def get_depth(symbol, type, pick=None, long_polling=None):
    """
    :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
    :param type: 可选值：{ percent, step1, step2, step3, step4, step5 }
    :param pick:
    :param long_polling: 可选值： { true, false }
    :return:
    """
    params = dict()
    params['symbol'] = symbol
    if type:
        params['type'] = type
    if pick:
        params['pick'] = pick
    if long_polling:
        params['long-polling'] = long_polling
    url = MARKET_URL + '/market/depth'
    return http_get_request(url, params)


def get_trade(symbol, pick=None, long_polling=None):
    """
    :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
    :param pick:
    :param long_polling: 可选值： { true, false }
    :return:
    """
    params = dict()
    params['symbol'] = symbol
    if pick:
        params['pick'] = pick
    if long_polling:
        params['long-polling'] = long_polling
    url = MARKET_URL + '/market/trade'
    return http_get_request(url, params)

'''
Trade/Account API
'''


def get_accounts_all(key_index="CNY_1", acct_type="spot"):
    path = "/v1/account/accounts"
    params = dict()
    if acct_type:
        params["type"] = acct_type
    return api_key_get(params, path, key_index=key_index)


def get_balance(acct_id, key_index="CNY_1"):
    if type(acct_id) is not str:
        acct_id = str(acct_id)
    url = "/v1/account/accounts/" + acct_id + "/balance"
    params = dict()
    params["account-id"] = acct_id
    return api_key_get(params, url, key_index=key_index)


def order(symbol, price, amount, order_type, acct_id, source='api', key_index="CNY_1"):
    """
    :param symbol:
    :param price:
    :param amount:
    :param order_type: ['buy-market', 'sell-market', 'buy-limit', 'sell-limit']
    :param acct_id:
    :param token:
    :param source: ['sys', 'web', 'api', 'app']
    :return:
    """
    if type(acct_id) is not str:
        acct_id = str(acct_id)
    if type(price) is not str:
        price = str(price)
    if type(amount) is not str:
        amount = str(amount)
    params = dict()
    params["account-id"] = acct_id
    params["amount"] = amount
    if order_type in ['buy-limit', 'sell-limit']:
        params["price"] = price
    params["symbol"] = symbol
    params["type"] = order_type
    params["source"] = source
    url = "/v1/order/orders"
    return api_key_post(params, url, key_index=key_index)


def place_order(order_id, key_index='CNY_1'):
    params = dict()
    if type(order_id) is not str:
        order_id = str(order_id)
    url = "/v1/order/orders/" + order_id + "/place"
    return api_key_post(params, url, key_index=key_index)


def cancel_order(order_id, key_index='CNY_1'):
    params = dict()
    url = "/v1/order/orders/" + order_id + "/submitcancel"
    return api_key_post(params, url, key_index=key_index)


def order_info(order_id, key_index='CNY_1'):
    params = dict()
    url = "/v1/order/orders/" + order_id
    return api_key_get(params, url, key_index=key_index)

'''
symbol true string 交易对 btccny
type false string 订单类型 buy-limit
start-date false string 查询开始日期参数, 日期格式yyyy-mm-dd 2017-03-16
end-date false string 查询结束日期参数, 日期格式yyyy-mm-dd 2019-03-16
states true string 订单状态组合，使用","分割 pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled
from false string 过滤数据ID起始范围 999999999
size false string 查询记录大小 20

'''


def orders_info_list(states, symbol, order_type=None, start_date=None, end_date=None, id_from=None, record_size=None, key_index='CNY_1'):
    params = dict()
    params['symbol'] = symbol
    params['states'] = states
    if order_type:
        params['type'] = order_type
    if start_date:
        params['start-date'] = start_date
    if end_date:
        params['end-date'] = end_date
    if id_from:
        params['from'] = id_from
    if record_size:
        params['size'] = record_size
    url = '/v1/order/orders'
    return api_key_get(params, url, key_index=key_index)


def active_orders(symbol, key_index="CNY_1"):
    states = 'submitted,partial-filled'
    return orders_info_list(states, symbol, key_index=key_index)

