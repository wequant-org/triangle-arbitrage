#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import io
import logging
import math
import sqlite3 as lite
import sys
import time
import traceback
import uuid

import pandas as pd

COIN_TYPE_BTC_CNY = "btc_cny"
COIN_TYPE_LTC_CNY = "ltc_cny"
COIN_TYPE_ETH_CNY = "eth_cny"
COIN_TYPE_LTC_BTC = 'ltc_btc'
COIN_TYPE_ETH_BTC = 'eth_btc'
HUOBI_COIN_TYPE_BTC = 1
HUOBI_COIN_TYPE_LTC = 2
HUOBI_COIN_TYPE_ETH = 3
COIN_TYPE_CNY = "cny"
COIN_TYPE_USD = "usd"
CONTRACT_TYPE_WEEK = "week"
CONTRACT_TYPE_NEXT_WEEK = "next_week"  # next_week只出现在比特币中
CONTRACT_TYPE_WEEK_AND_NEXT_WEEK = "week_and_next_week"
CONTRACT_TYPE_QUARTER = "quarter"  # 目前不支持
BITVC_MIN_CASH_AMOUNT = 100  # bitvc的最小下单金额
HUOBI_BTC_MIN_ORDER_QTY = 0.001
HUOBI_BTC_MIN_ORDER_CASH = 1.0
HUOBI_LTC_MIN_ORDER_QTY = 0.01
HUOBI_LTC_MIN_ORDER_CASH = 1.0
BITEX_ETH_MIN_ORDER_QTY = 0.001
BITEX_ETH_MIN_ORDER_CASH = 1.0
OKCOIN_BTC_MIN_ORDER_QTY = 0.01
OKCOIN_LTC_MIN_ORDER_QTY = 0.1
CHBTC_ETH_MIN_ORDER_QTY = 0.001
PRO_ETH_BTC_MIN_ORDER_QTY = 0.00001
PRO_LTC_BTC_MIN_ORDER_QTY = 0.00001
POLO_MIN_ORDER_BTC_AMOUNT = 0.0001
DATA_DEPTH = 150

HUOBI_SPOT_TRANSACTION_FEE = 0.002  # huobi现货手续费
OKCOIN_SPOT_TRANSACTION_FEE = 0.002  # okcoin现货手续费
BITVC_FEE_RATE = 0.0003  # # bitvc开仓手续费比例（请勿随意更改）

# huobi 订单返回信息中，type字段
HUOBI_ORDER_TYPE_BUY_LIMIT = 1
HUOBI_ORDER_TYPE_SELL_LIMIT = 2
HUOBI_ORDER_TYPE_BUY_MARKET = 3
HUOBI_ORDER_TYPE_SELL_MARKET = 4

# (开多: orderType 1 tradeType 1 开空: orderType 1 tradeType 2)
# (平多: orderType 2 tradeType 2 平空: orderType 2 tradeType 1)
CONTRACT_ORDER_TYPE_OPEN = 1
CONTRACT_ORDER_TYPE_CLOSE = 2
CONTRACT_ORDER_TYPE_OPEN_STRING = "open"
CONTRACT_ORDER_TYPE_CLOSE_STRING = "close"
CONTRACT_TRADE_TYPE_BUY = 1
CONTRACT_TRADE_TYPE_SELL = 2

HUOBI = "huobi"
OKCOIN = "okcoin"
BITVC = "bitvc"
BITEX = "bitex"
CHBTC = "chbtc"
POLO = "polo"
PRO = "pro"
HUOBI_MARKET_TYPE = 1
OKCOIN_MARKET_TYPE = 2
BITEX_MARKET_TYPE = 3
CHBTC_MARKET_TYPE = 4
PRO_MARKET_TYPE = 5
POLO_MARKET_TYPE = 6
SPOT_TRADE_TYPE_BUY = "buy"
SPOT_TRADE_TYPE_SELL = "sell"
ORDER_TYPE_LIMIT_ORDER = "limit_order"
ORDER_TYPE_MARKET_ORDER = "market_order"

BITVC_DYNAMIC_RIGHTS = "dynamicRights"
BITVC_STATIC_RIGHTS = "staticRights"

HUOBI_CNY_BTC = "huobi_cny_btc"
HUOBI_CNY_LTC = "huobi_cny_ltc"
HUOBI_USD_BTC = "huobi_usd_btc"
HUOBI_CNY_CASH = "huobi_cny_cash"
HUOBI_USD_CASH = "huobi_usd_cash"

OKCOIN_CNY_BTC = "okcoin_cny_btc"
OKCOIN_CNY_LTC = "okcoin_cny_ltc"
OKCOIN_USD_BTC = "okcoin_usd_btc"
OKCOIN_USD_LTC = "okcoin_usd_ltc"
OKCOIN_CNY_CASH = "okcoin_cny_cash"
OKCOIN_USD_CASH = "okcoin_usd_cash"

BITVC_CNY_BTC = "bitvc_cny_btc"
BITVC_CNY_LTC = "bitvc_cny_ltc"
BITVC_USD_BTC = "bitvc_usd_btc"
BITVC_USD_LTC = "bitvc_usd_ltc"
BITVC_CNY_CASH = "bitvc_cny_cash"
BITVC_USD_CASH = "bitvc_usd_cash"

# bitvc下周合约开始于周四
BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY = 3
# bitvc下周合约开始于中午12：00
BITVC_NEXT_WEEK_CONTRACT_START_TIME = datetime.time(12, 0)

# bitvc下周合约结束于周五
BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY = 4
# bitvc下周合约结束于中午12：00
BITVC_NEXT_WEEK_CONTRACT_END_TIME = datetime.time(12, 0)

HUOBI_ORDER_STATUS_INFO = ["unfilled", "partially filled", "fully filled", "cancelled", "abandoned", "abnormal",
                           "partially cancelled", "queuing"]

OKCOIN_ORDER_STATUS_INFO = ["unfilled", "partially filled", "fully filled", "cancelling", "cancelled"]

coinTypeStructure = {
    COIN_TYPE_BTC_CNY: {
        "huobi": {
            "coin_type": HUOBI_COIN_TYPE_BTC,
            "market": COIN_TYPE_CNY,
            "coin_str": HUOBI_CNY_BTC,
            "market_str": HUOBI_CNY_CASH
        },
        "okcoin": {
            "coin_type": COIN_TYPE_BTC_CNY,
            "market": COIN_TYPE_CNY,
            "coin_str": OKCOIN_CNY_BTC,
            "market_str": OKCOIN_CNY_CASH
        },
        "bitvc": {
            "coin_type": HUOBI_COIN_TYPE_BTC,
            "market": COIN_TYPE_CNY,
            "coin_str": BITVC_CNY_BTC,
            "market_str": BITVC_CNY_CASH
        }

    },
    COIN_TYPE_LTC_CNY: {
        "huobi": {
            "coin_type": HUOBI_COIN_TYPE_LTC,
            "market": COIN_TYPE_CNY,
            "coin_str": HUOBI_CNY_LTC,
            "market_str": HUOBI_CNY_CASH
        },
        "okcoin": {
            "coin_type": COIN_TYPE_LTC_CNY,
            "market": COIN_TYPE_CNY,
            "coin_str": OKCOIN_CNY_LTC,
            "market_str": OKCOIN_CNY_CASH
        }
    }
}


# 从huobi style的security拿到okcoin style的security
def getCoinMarketTypeFromSecurity(security):
    if security == "huobi_cny_btc":
        return COIN_TYPE_BTC_CNY
    elif security == "huobi_cny_ltc":
        return COIN_TYPE_LTC_CNY
    else:
        raise ValueError("invalid security %s" % security)


# 向下取小数点后decimal_places位精度
def downRound(qty, decimal_places=4):
    a = "%f" % qty
    b = a.split('.')
    round_down = '%s.%s' % (b[0], b[1][:decimal_places])
    return float(round_down)

# 对币数量进行精度裁剪
def getRoundedQuantity(qty, coin_type):
    if coin_type == COIN_TYPE_BTC_CNY:
        # 按照okcoin的下单规则，比特币都是0.01 btc的整数倍，取下限
        return downRound(qty, decimal_places=2)
    elif coin_type == COIN_TYPE_LTC_CNY:
        # 按照okcoin的下单规则，莱特币都是0.1 ltc的整数倍，取下限
        return downRound(qty, decimal_places=1)
    elif coin_type == COIN_TYPE_ETH_BTC:
        return downRound(qty, decimal_places=4)
    elif coin_type == COIN_TYPE_LTC_BTC:
        return downRound(qty, decimal_places=4)
    else:
        raise ValueError("invalid coin type %s" % coin_type)


# 从对象拿数据
def componentExtract(object, key, default=None):
    if type(object) == dict:
        return object.get(key, default)
    else:
        return getattr(object, key, default)


# 获取uuid
def getUUID():
    return str(uuid.uuid1())


# print traceback to log
def printTracebackToLog(timeLog):
    timeLog(traceback.format_exc())


# 获取当前时间，返回字符串，格式为：'YYYYMMDD_hhmmss'
def current_time_str():
    current_time = datetime.datetime.now()
    time_string = current_time.strftime('%Y%m%d_%H%M%S')
    return time_string


# 将时间戳转化为可读时间
def timestamp_to_timestr(timestamp):
    time_struct = time.localtime(timestamp)
    time_string = time.strftime("%Y%m%d_%H%M%S", time_struct)
    return time_string


# 抽象出timelogger
class TimeLogger(object):
    def __init__(self, logFileName):
        self.timeLogger = logging.getLogger('timeLog')
        self.timeLogger.setLevel(logging.DEBUG)
        self.timeLogHandler = logging.FileHandler(logFileName)
        self.timeLogHandler.setLevel(logging.DEBUG)
        self.consoleLogHandler = logging.StreamHandler()
        self.consoleLogHandler.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.timeLogHandler.setFormatter(formatter)
        self.consoleLogHandler.setFormatter(formatter)
        # 给timeLogger添加handler
        self.timeLogger.addHandler(self.timeLogHandler)
        self.timeLogger.addHandler(self.consoleLogHandler)

    def timeLog(self, content, level=logging.INFO):
        if level == logging.DEBUG:
            self.timeLogger.debug(content)
        elif level == logging.INFO:
            self.timeLogger.info(content)
        elif level == logging.WARN:
            self.timeLogger.warn(content)
        elif level == logging.ERROR:
            self.timeLogger.error(content)
        elif level == logging.CRITICAL:
            self.timeLogger.critical(content)
        else:
            raise ValueError("unsupported logging level %d" % level)

# 计算时间差
def diff_times_in_seconds(t1, t2):
    # caveat emptor - assumes t1 & t2 are python times, on the same day and t2 is after t1
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60*h1)
    t2_secs = s2 + 60 * (m2 + 60*h2)
    return( t2_secs - t1_secs)

# 从数据库中获取调仓信息
def get_trans_record(coinMarketType):
    con = lite.connect('orderBook.db')
    trans_sql = ("select *, datetime(record_time, 'unixepoch', 'localtime') as time_str "
                 "from depth_data_%s order by record_time" % coinMarketType)
    trans_record = pd.read_sql(trans_sql, con, index_col='time_str', parse_dates=['time_str'])
    trans_record.to_csv(
        "data/depth_data/depth_data_%s_%s.csv" % (coinMarketType, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))
    return trans_record


# 从数据库中获取pos record信息
def get_pos_record():
    con = lite.connect('orderBook.db')
    pos_sql = ("select *, datetime(record_time, 'unixepoch', 'localtime') as time_str "
               "from positionRecord order by record_time")
    pos_record = pd.read_sql(pos_sql, con, index_col='time_str', parse_dates=['time_str'])
    pos_record.to_csv("data/pos_data/pos_data_%s.csv" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))
    return pos_record


# 查看所给时间是否有bitvc的下周合约
def has_bitvc_next_week_contract(current_datetime):
    """
    测试所给时间是否有bitvc的下周合约
    :param current_datetime: 一个datetime.datetime对象
    :return: 有则返回True， 否则返回False
    """
    current_weekday = current_datetime.weekday()
    current_time = current_datetime.time()
    if BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY <= current_weekday <= BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY:
        if current_weekday == BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY:
            if current_time <= BITVC_NEXT_WEEK_CONTRACT_START_TIME:
                return False
        if current_weekday == BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY:
            if current_time >= BITVC_NEXT_WEEK_CONTRACT_END_TIME:
                return False
        return True
    return False


# 查看所给时间，是否在本周的某一个时间段内
def in_time_period(current_datetime, start_week_day, end_week_day, start_time, end_time):
    """
    测试所给时间是否在某一个时间段内
    :param current_datetime: 一个datetime.datetime对象
    :return: 有则返回True， 否则返回False
    """
    current_weekday = current_datetime.weekday()
    current_time = current_datetime.time()
    if start_week_day <= current_weekday <= end_week_day:
        if current_weekday == start_week_day:
            if current_time < start_time:
                return False
        if current_weekday == end_week_day:
            if current_time >= end_time:
                return False
        return True
    return False


# 策略进程
def start_strat(strat, exitOnException=False):
    if strat.dailyExitTime is not None:
        # check whether current time is after the dailyExitTime, if yes, exit
        while datetime.datetime.now() <= datetime.datetime.strptime(
                                datetime.date.today().strftime("%Y-%m-%d") + " " + strat.dailyExitTime,
                "%Y-%m-%d %H:%M:%S"):
            try:
                strat.go()
            except Exception:
                printTracebackToLog(strat.timeLog)
                if exitOnException:
                    return
        strat.timeLog("抵达每日终结时间：%s, 现在退出." % strat.dailyExitTime)
    else:
        while True:
            try:
                strat.go()
            except Exception:
                printTracebackToLog(strat.timeLog)
                if exitOnException:
                    return
