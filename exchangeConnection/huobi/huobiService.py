#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exchangeConnection.huobi.util import *
from utils.helper import *

'''
获取账号详情
'''


def getAccountInfo(market, method, key_index='CNY_1'):
    params = {"method": method}
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
获取所有正在进行的委托
'''


def getOrders(coinType, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
获取订单详情
@param coinType
@param id
'''


def getOrderInfo(coinType, id, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['id'] = id
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
限价买入
@param coinType
@param price
@param amount
@param tradePassword
@param tradeid
@param method
'''


def buy(coinType, price, amount, tradePassword, tradeid, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['price'] = price
    params['amount'] = amount
    extra = {}
    extra['trade_password'] = tradePassword
    extra['trade_id'] = tradeid
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
限价卖出
@param coinType
@param price
@param amount
@param tradePassword
@param tradeid
'''


def sell(coinType, price, amount, tradePassword, tradeid, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['price'] = price
    params['amount'] = amount
    extra = {}
    extra['trade_password'] = tradePassword
    extra['trade_id'] = tradeid
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
市价买
@param coinType
@param amount
@param tradePassword
@param tradeid
'''


def buyMarket(coinType, amount, tradePassword, tradeid, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['amount'] = amount
    extra = {}
    extra['trade_password'] = tradePassword
    extra['trade_id'] = tradeid
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
市价卖出
@param coinType
@param amount
@param tradePassword
@param tradeid
'''


def sellMarket(coinType, amount, tradePassword, tradeid, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['amount'] = amount
    extra = {}
    extra['trade_password'] = tradePassword
    extra['trade_id'] = tradeid
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
查询个人最新10条成交订单
@param coinType
'''


def getNewDealOrders(coinType, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
根据trade_id查询oder_id
@param coinType
@param tradeid
'''


def getOrderIdByTradeId(coinType, tradeid, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['trade_id'] = tradeid
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
撤销订单
@param coinType
@param id
'''


def cancelOrder(coinType, id, market, method, key_index='CNY_1'):
    params = {"method": method}
    params['coin_type'] = coinType
    params['id'] = id
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


'''
获取实时行情
@param coinType #币种 1 比特币 2 莱特币
'''


def getTicker(coinType, market):
    if market == COIN_TYPE_CNY:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/staticmarket/ticker_btc_json.js"
        else:
            url = "http://api.huobi.com/staticmarket/ticker_ltc_json.js"
    elif market == COIN_TYPE_USD:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/usdmarket/ticker_btc_json.js"
        else:
            raise ValueError("invalid coinType %d for market %s" % (coinType, market))
    else:
        raise ValueError("invalid market %s" % market)
    return httpRequest(url, {})


'''
获取实时行情
@param coinType:币种 1 比特币 2 莱特币
@param depth_size:指定深度
'''


def getDepth(coinType, market, depth_size=5):
    if market == COIN_TYPE_CNY:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/staticmarket/depth_btc_" + str(depth_size) + ".js"
        else:
            url = "http://api.huobi.com/staticmarket/depth_ltc_" + str(depth_size) + ".js"
    elif market == COIN_TYPE_USD:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/usdmarket/depth_btc_" + str(depth_size) + ".js"
        else:
            raise ValueError("invalid coinType %d for market %s" % (coinType, market))
    else:
        raise ValueError("invalid market %s" % market)
    return httpRequest(url, {})


'''
获取最少订单数量
@param coinType:币种 1 比特币 2 莱特币
火币上比特币交易及莱特币交易都是0.0001的整数倍
比特币最小交易数量：0.001,莱特币最小交易数量：0.01
'''


def getMinimumOrderQty(coinType):
    if coinType == HUOBI_COIN_TYPE_BTC:
        return 0.001
    else:
        return 0.01


'''
获取最少交易金额
火币上比特币交易及莱特币交易金额都是0.01的整数倍
最小交易金额：1
'''


def getMinimumOrderCashAmount():
    return 1


'''
提取BTC/LTC
提币数量 BTC>=0.01 LTC>=0.1
withdraww_fee: 网络转账手续费，支持范围：BTC[0.0001,0.01],LTC目前仅支持0.01。如果不填此参数默认最小值
'''


def withdrawCoin(coinType, amount, address, tradePassword, market, fee,method, key_index='CNY_1'):
    params = {"method": method}
    params["withdraw_amount"] = amount
    params['coin_type'] = coinType
    params["withdraw_address"] = address
    extra = {}
    extra['trade_password'] = tradePassword
    extra['market'] = market
    extra["withdraw_fee"] = fee
    res = send2api(params, extra, key_index=key_index)
    return res

# 查询提币执行情况
def withdraw_info(withdraw_id, market, key_index='CNY_1'):
    method = "get_withdraw_coin_result"
    params = {"method": method}
    params["withdraw_coin_id"] = withdraw_id
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


def get_prices(coin_type, frequency, length=300):
    """
    支持1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M, 1y频率的信息
    返回一个 pandas.DataFrame 对象，结构为
                open    high    low    close    volume
    bar_time

    :param coin_type:
    :param frequency:
    :param length:
    :return:
    """
    api_frequency = frequency
    aggregation_level = 1
    if frequency == "4h":
        api_frequency = "60m"
        aggregation_level = 4
    hist = getKLine(coin_type, api_frequency, length=length * aggregation_level)
    hist_pd = convert_to_ohlcv_dataframe(hist)
    if frequency == "4h":
        hist_pd = aggregation(hist_pd)
    return hist_pd


# 聚合
def aggregation(df):
    ohlc = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'}
    new_pd = df.resample('240min', closed='left', label='left').apply(ohlc).ffill()
    return new_pd


def convert_to_ohlcv_dataframe(data_array):
    date_format = "%Y%m%d%H%M%S000"
    df = pd.DataFrame(data_array, columns=['bar_time', 'open', 'high', 'low', 'close', 'volume'], )
    df.index = pd.to_datetime(df.bar_time, format=date_format, utc=True)
    del df['bar_time']
    return df


# 获取历史行情信息(huobi api接口，未处理)
def getKLine(coinType, frequency,length=300, market=COIN_TYPE_CNY):
    """
    直接实现huobi api接口，只能接受1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M, 1y频率的信息
    返回一个6维数组，包括 time, open, high, low, close, volume
    :param coinType: HUOBI_COIN_TYPE_BTC or HUOBI_COIN_TYPE_LTC
    :param frequency: 1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M, 1y
    :param length:
    :param market: COIN_TYPE_CNY or COIN_TYPE_USD
    :return:
    """
    if frequency == "1m":
        period = "001"
    elif frequency == "5m":
        period = "005"
    elif frequency == "15m":
        period = "015"
    elif frequency == "30m":
        period = "030"
    elif frequency == "60m":
        period = "060"
    elif frequency == "1d":
        period = "100"
    elif frequency == "1w":
        period = "200"
    elif frequency == "1M":
        period = "300"
    elif frequency == "1y":
        period = "400"
    else:
        raise ValueError("invalid frequency %s" % frequency)

    if market == COIN_TYPE_CNY:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/staticmarket/btc_kline_%s_json.js?length=%s" % (period, length)
        else:
            url = "http://api.huobi.com/staticmarket/ltc_kline_%s_json.js?length=%s" % (period, length)
    elif market == COIN_TYPE_USD:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/usdmarket/btc_kline_%s_json.js?length=%s" % (period, length)
        else:
            raise ValueError("invalid coinType %d for market %s" % (coinType, market))
    else:
        raise ValueError("invalid market %s" % market)
    return httpRequest(url, {})


# 获取最新的买卖盘数据
def get_orderbook(coinType, market):
    if market == COIN_TYPE_CNY:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/staticmarket/detail_btc_json.js"
        else:
            url = "http://api.huobi.com/staticmarket/detail_ltc_json.js"
    elif market == COIN_TYPE_USD:
        if coinType == HUOBI_COIN_TYPE_BTC:
            url = "http://api.huobi.com/usdmarket/detail_btc_json.js"
        else:
            raise ValueError("invalid coinType %d for market %s" % (coinType, market))
    else:
        raise ValueError("invalid market %s" % market)
    return httpRequest(url, {})

# 获取最近60笔市场成交信息
def get_latest_trades(coinType, market="cny"):
    orderbook = get_orderbook(coinType, market)
    trades_data = orderbook["trades"]
    trades_df = pd.DataFrame(trades_data)
    trades_df = trades_df.set_index("time")
    trades_df.sort_index(inplace=True)
    return trades_df

