#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib.parse
import urllib.request

import requests

import accountConfig

BROKER_URL = 'http://be.huobi.com/v1/'
MARKET_URL = 'http://be.huobi.com/market/'


def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=5)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpGet failed, detail is:%s" % response.text)


def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpPost failed, detail is:%s" % response.text)


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
    url = MARKET_URL + 'kline'
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
    url = MARKET_URL + 'depth'
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
    url = MARKET_URL + 'trade'
    return http_get_request(url, params)

def login(login_name, password, application='WEB'):
    params = dict()
    params['application'] = application
    params['login-name'] = login_name
    params['password'] = password
    url = BROKER_URL + "login"
    return http_post_request(url, params)

def verify_token(token):
    params = dict()
    params['token'] = token
    url = BROKER_URL + 'users/token/verify'
    return http_post_request(url, params)

def get_accounts_all(token, acct_type=None):
    url = BROKER_URL + "account/accounts"
    params = dict()
    if acct_type:
        params["type"] = acct_type
    headers = {"Token": token}
    return http_get_request(url, params, add_to_headers=headers)

# 未测试
def get_balance(token, acct_id):
    if type(acct_id) is not str:
        acct_id = str(acct_id)
    url = BROKER_URL + "account/accounts/" + acct_id + "/balance"
    params = dict()
    params["account-id"] = acct_id
    headers = {"Token": token}
    return http_get_request(url, params, add_to_headers=headers)

def order(symbol, price, amount, order_type, acct_id, token, auth_data, source='api'):
    """
    :param symbol:
    :param price: None or number
    :param amount:
    :param order_type: ['buy-market', 'sell-market', 'buy-limit', 'sell-limit']
    :param acct_id:
    :param token:
    :param source: ['sys', 'web', 'api', 'app']
    :return:
    """
    if type(acct_id) is not str:
        acct_id = str(acct_id)
    if price and (type(price) is not str):
        price = str(price)
    if type(amount) is not str:
        price = str(amount)
    params = dict()
    headers = {"Token": token}
    headers.update({"AuthData": auth_data})
    params["account-id"] = acct_id
    params["amount"] = amount
    if price:
        params["price"] = price
    else:
        params["price"] = ''
    params["symbol"] = symbol
    params["type"] = order_type
    params["source"] = source
    url = BROKER_URL + "order/orders"
    return http_post_request(url, params, add_to_headers=headers)

def place_order(order_id, token, auth_data):
    params = dict()
    headers = {"Token": token}
    headers.update({"AuthData": auth_data})
    if type(order_id) is not str:
        order_id = str(order_id)
    url = BROKER_URL + "order/orders/" + order_id + "/place"
    return http_post_request(url, params, add_to_headers=headers)

def cancel_order(order_id, token, auth_data):
    params = dict()
    headers = {"Token": token}
    headers.update({"AuthData": auth_data})
    url = BROKER_URL + "order/orders/" + order_id + "/submitcancel"
    return http_post_request(url, params, add_to_headers=headers)

def order_info(order_id, token):
    params = dict()
    headers = {"Token": token}
    url = BROKER_URL + "order/orders/" + order_id
    return http_get_request(url, params, add_to_headers=headers)

'''
symbol true string 交易对 btccny
type false string 订单类型 buy-limit
start-date false string 查询开始日期参数, 日期格式yyyy-mm-dd 2017-03-16
end-date false string 查询结束日期参数, 日期格式yyyy-mm-dd 2019-03-16
states true string 订单状态组合，使用","分割 pre-submitted,submitted,partial-filled,partial-canceled,filled,canceled
from false string 过滤数据ID起始范围 999999999
size false string 查询记录大小 20

'''
def orders_info_list(token, states, symbol, order_type=None, start_date=None, end_date=None, id_from=None, record_size=None):
    headers = {"Token": token}
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
    url = BROKER_URL + 'order/orders'
    return http_get_request(url, params, add_to_headers=headers)

# states不太确定
def active_orders(token, symbol):
    states = 'pre-submitted,submitted,partial-filled'
    return orders_info_list(token, states, symbol)


def auth_verify(token, auth_data, auth_type):
    headers = {"Token": token}
    params = dict()
    params["auth-data"] = auth_data
    params["auth-type"] = auth_type
    url = BROKER_URL + "users/auth/verify"
    return http_post_request(url, params, add_to_headers=headers)
