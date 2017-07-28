#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exchangeConnection.huobi.huobiService
import exchangeConnection.bitex.bitexService
import exchangeConnection.pro.proService
import utils.helper as uh


# 包装一个不同市场的统一接口 方便同一套套利
class Market:
    def __init__(self, market_name="huobi"):
        self.market_name = market_name

    def market_detail(self, base_cur, quote_cur):
        """
        获取市场盘口信息
        :param base_cur:
        :param quote_cur:
        :return:
        """
        if self.market_name == "huobi":
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey().get_depth("ethcny","step0").get("tick")
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey().get_depth("etccny", "step0").get(
                        "tick")
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.getDepth(uh.HUOBI_COIN_TYPE_BTC, quote_cur)
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.getDepth(uh.HUOBI_COIN_TYPE_LTC, quote_cur)
                else:
                    return None
            elif quote_cur == "btc":
                if base_cur == "eth":
                    return exchangeConnection.pro.proService.ProServiceAPIKey().get_depth("ethbtc").get("tick")
                elif base_cur == "etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey().get_depth("etcbtc").get("tick")
                elif base_cur == "ltc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey().get_depth("ltcbtc").get("tick")
                elif base_cur == "cny":
                    return exchangeConnection.huobi.huobiService.getDepth(uh.HUOBI_COIN_TYPE_BTC, "cny")
            else:
                return None
        else:
            return None

    def account_available(self, cur_name, cur_market_name):
        """
        获取某个currency的可用量
        :param cur_name:
        :param cur_market_name:
        :return:
        """
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth" or base_cur=="etc":
                    bitex_acc = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1").get_spot_acct_info()
                    if cur_name == "eth":
                        return float(bitex_acc.get("data").get("list")[2].get("balance"))
                    elif cur_name == "etc":
                        return float(bitex_acc.get("data").get("list")[2].get("balance"))
                    elif cur_name == "cny":
                        return float(bitex_acc.get("data").get("list")[0].get("balance"))
                elif base_cur == "btc" or base_cur == "ltc":
                    account_info = exchangeConnection.huobi.huobiService.getAccountInfo("cny", "get_account_info")
                    return float(account_info.get("available_{0}_display".format(cur_name)))
                else:
                    return None

            elif quote_cur == "btc":
                # 内测
                pro_acc = exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1").get_spot_acct_info()
                if cur_name == "btc":
                    return float(pro_acc.get("data").get("list")[0].get("balance"))
                elif cur_name == "eth":
                    return float(pro_acc.get("data").get("list")[2].get("balance"))
                elif cur_name == "etc":
                    return float(pro_acc.get("data").get("list")[2].get("balance"))
                elif cur_name == "ltc":
                    return float(pro_acc.get("data").get("list")[4].get("balance"))
                else:
                    return None
            else:
                return None

    def buy(self, cur_market_name, price, amount):
        # print("buy", cur_market_name, price, amount)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("ethcny", price, amount, 'buy-limit')
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("etccny", price, amount, 'buy-limit')
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.buy(1, price, amount, None, None, "cny", "buy")
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.buy(2, price, amount, None, None, "cny", "buy")
            elif quote_cur == "btc":
                if base_cur == "eth":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .order("ethbtc", price, amount, 'buy-limit')
                elif base_cur == "etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .order("etcbtc", price, amount, 'buy-limit')
                elif base_cur == "ltc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ltcbtc", price, amount, 'buy-limit')
            else:
                return None

    def sell(self, cur_market_name, price, amount):
        # print("sell", cur_market_name, price, amount)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("ethcny", price, amount, 'sell-limit')
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("etccny", price, amount, 'sell-limit')
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.sell(1, price, amount, None, None, "cny", "sell")
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.sell(2, price, amount, None, None, "cny", "sell")
            elif quote_cur == "btc":
                if base_cur == "ltc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ltcbtc", price, amount, 'sell-limit')
                elif base_cur == "eth":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ethbtc", price, amount, 'sell-limit')
                elif base_cur == "etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("etcbtc", price, amount, 'sell-limit')
            else:
                return None

    def buy_market(self, cur_market_name, amount):
        """
        市价买
        :param cur_market_name: 货币对的名称
        :param amount: 买的总价
        :return:
        """
        # print("buy_market:", cur_market_name, amount)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("ethcny", 0.0, amount, 'buy-market')
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("etccny", 0.0, amount, 'buy-market')
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.buyMarket(1, amount, None, None, "cny", "buy_market")
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.buy(2, amount, None, None, "cny", "buy_market")
            elif quote_cur == "btc":
                if base_cur == "eth":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .order("ethbtc", 0.0, amount, 'buy-market')
                elif base_cur == "etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .order("etcbtc", 0.0, amount, 'buy-market')
                elif base_cur == "ltc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ltcbtc", 0.0, amount, 'buy-market')
            else:
                return None

    def sell_market(self, cur_market_name, amount):
        """
        市价卖
        :param cur_market_name: 货币对的名称
        :param amount: 卖的数量
        :return:
        """
        # print("sell_market:", cur_market_name, amount)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("ethcny", 0.0, amount, 'sell-market')
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").order("etccny", 0.0, amount, 'sell-market')
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.buyMarket(1, amount, None, None, "cny", "sell_market")
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.buy(2, amount, None, None, "cny", "sell_market")
            elif quote_cur == "btc":
                if base_cur == "ltc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ltcbtc", 0.0, amount, 'sell-market')
                elif base_cur == "eth":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("ethbtc", 0.0, amount, 'sell-market')
                elif base_cur == "etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1") \
                        .order("etcbtc", 0.0, amount, 'sell-market')
            else:
                return None

    def order_normal(self, order_result, cur_market_name):
        """
        是否成功下单
        :param order_result: 下单返回结果
        :param cur_market_name: 货币对名称
        :return:
        """
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth" or base_cur == "etc":
                    if order_result.get("status") == "ok":
                        return True
                    else:
                        return False
                elif base_cur == "btc" or "ltc":
                    if order_result.get("result") == "success":
                        return True
                    else:
                        return False
            elif quote_cur == "btc":
                if base_cur == "ltc" or "eth" or "etc":
                    if order_result.get("status") == "ok":
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return None

    def get_order_processed_amount(self, order_result, cur_market_name):
        # print("get_order_processed_amount:", order_result, cur_market_name)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").get_order_info(order_result.get("data"))
                    return result.get("data").get("field-amount")
                elif base_cur == "etc":
                    result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").get_order_info(order_result.get("data"))
                    return result.get("data").get("field-amount")
                elif base_cur == "btc":
                    result = exchangeConnection.huobi.huobiService.getOrderInfo(
                        1, order_result.get("id"), "cny", "order_info")
                    return result.get("processed_amount")
                elif base_cur == "ltc":
                    result = exchangeConnection.huobi.huobiService.getOrderInfo(
                        2, order_result.get("id"), "cny", "order_info")
                    return result.get("processed_amount")
            elif quote_cur == "btc":
                if base_cur == "ltc" or base_cur == "eth" or base_cur == "etc":
                    result = exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .get_order_info(order_result.get("data"))
                    return result.get("data").get("field-amount")
                else:
                    return None
            else:
                return None

    def cancel_order(self, order_result, cur_market_name):
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1")\
                        .cancel_order(str(order_result.get("data")))  # {'status': 'ok', 'data': '2705970'}
                elif base_cur == "etc":
                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1")\
                        .cancel_order(str(order_result.get("data")))  # {'status': 'ok', 'data': '2705970'}
                elif base_cur == "btc":
                    return exchangeConnection.huobi.huobiService.cancelOrder(
                        1, order_result.get("id"), "cny", "cancel_order")
                elif base_cur == "ltc":
                    return exchangeConnection.huobi.huobiService.cancelOrder(
                        2, order_result.get("id"), "cny", "cancel_order")
            elif quote_cur == "btc":
                if base_cur == "ltc" or base_cur == "eth" or base_cur =="etc":
                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1").cancel_order(
                           order_result.get("data"))
            else:
                return None

    def get_order_status(self, order_result, cur_market_name):
        # print("get_order_status:", order_result, cur_market_name)
        if self.market_name == "huobi":
            base_cur, quote_cur = cur_market_name.split("_")
            if quote_cur == "cny":
                if base_cur == "eth":
                    result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").get_order_info(order_result.get("data"))
                    return result.get("data").get("state")
                elif base_cur == "etc":
                    result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
                        key_index="CNY_1").get_order_info(order_result.get("data"))
                    return result.get("data").get("state")
                elif base_cur == "btc":
                    result = exchangeConnection.huobi.huobiService.getOrderInfo(
                        1, order_result.get("id"), "cny", "order_info")
                    return result.get("status")
                elif base_cur == "ltc":
                    result = exchangeConnection.huobi.huobiService.getOrderInfo(
                        2, order_result.get("id"), "cny", "order_info")
                    return result.get("status")
            elif quote_cur == "btc":
                if base_cur == "ltc" or base_cur == "eth" or base_cur=="etc":
                    result = exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
                        .get_order_info(order_result.get("data"))
                    return result.get("data").get("state")
                else:
                    return None
            else:
                return None


# test
if __name__ == "__main__":
    huobi = Market()
# print(huobi.market_detail("eth", "cny"))
# print(huobi.market_detail("btc", "cny"))
# print(huobi.market_detail("ltc", "cny"))
# print(huobi.market_detail("eth", "btc"))
# print(huobi.market_detail("ltc", "btc"))
# print(exchangeConnection.pro.proService.ProServiceAPIKey().get_depth("ethcny").get("tick"))
# print("以太币账户：",exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1").get_spot_acct_info())
# print("以太币可用", huobi.account_available("cny", "eth_cny"))
# print(exchangeConnection.huobi.huobiService.getAccountInfo("cny", "get_account_info"))
# print(exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1").get_spot_acct_info())
# result = exchangeConnection.huobi.huobiService.buy(2, 320.90, 0.4, None, None, "cny", "buy")
# print(result)
# {'result': 'success', 'id': 4491600137}
# result = exchangeConnection.huobi.huobiService.cancelOrder(1,4491600137, "cny", "cancel_order")
# print(result)
# print(exchangeConnection.huobi.huobiService.getOrderInfo(1, result.get("id"), "cny", "order_info"))
# {'id': 4491348833, 'type': 1, 'order_price': '20000.00', 'order_amount': '0.0020', 'processed_price': '19997.98', 'processed_amount': '0.0020', 'vot': '39.99', 'fee': '0.0000', 'total': '39.99', 'status': 2}

# result = exchangeConnection.huobi.huobiService.buyMarket(1, 2000, None, None, "cny", "buy_market")
# print(result)
# 买入eth
# result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
#                         key_index="CNY_1").order("ethcny", 4000, 0.01, 'buy-limit')
# print("买入eth", result)  # {'status': 'ok', 'data': '2705107'}
# result = {'status': 'ok', 'data': '2706194'}
# print(exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1").get_order_info(result.get("data")))
# print("eth order:", exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1").get_active_orders("ethcny"))
# print("eth cancel order:", exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="CNY_1").cancel_order("2705970"))
# result = exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
#                         key_index="CNY_1").order("ethcny", 11.0, 0.01, 'buy-market')
# print(result)

#pro
# print(exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1").get_spot_acct_info())
# print(exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
#                         .order("ethbtc", 1.001, 0.01, 'buy-limit'))
# order_result = {'status': 'ok', 'data': '51'}
# print(exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1")\
#                         .get_order_info(order_result.get("data")).get("data").get("field-amount"))
# print(exchangeConnection.pro.proService.ProServiceAPIKey(key_index="CNY_1").cancel_order(order_result.get("data")))
# order_result = {'status': 'ok', 'data': '3075505'}
# print(exchangeConnection.bitex.bitexService.BitexServiceAPIKey(
#                         key_index="CNY_1").get_order_info(order_result.get("data")).get("data"))
