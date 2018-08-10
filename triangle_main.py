#!/usr/bin/env python
# -*- coding: utf-8 -*-

import marketHelper
# 设定账户 accountConfig
import traceback
import time
import logging
# import yaml
import multiprocessing
import math
from utils.helper import *

# 设置logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
main_log_handler = logging.FileHandler("log/triangle_main_{0}.log".format(int(time.time())), mode="w", encoding="utf-8")
main_log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
main_log_handler.setFormatter(formatter)
logger.addHandler(main_log_handler)


class Triangle:
    """
        交易对：用一种资产（quote currency）去定价另一种资产（base currency）,比如用比特币（BTC）去定价莱特币（LTC），
        就形成了一个LTC/BTC的交易对，
        交易对的价格代表的是买入1单位的base currency（比如LTC）
        需要支付多少单位的quote currency（比如BTC），
        或者卖出一个单位的base currency（比如LTC）
        可以获得多少单位的quote currency（比如BTC）。
        当LTC对BTC的价格上涨时，同等单位的LTC能够兑换的BTC是增加的，而同等单位的BTC能够兑换的LTC是减少的。
    """
    def __init__(self, base_cur="ltc", quote_cur="btc", mid_cur="cny", interval=10):
        """
        初始化
        :param base_cur:  基准资产
        :param quote_cur:  定价资产
        :param mid_cur:  中间资产
        :param interval:  策略触发间隔
        """

        # 设定套利监控交易对
        self.base_cur = base_cur
        self.quote_cur = quote_cur
        self.mid_cur = mid_cur   # 中间货币，cny或者btc

        self.base_quote_slippage = 0.002  # 设定市场价滑点百分比
        self.base_mid_slippage = 0.002
        self.quote_mid_slippage = 0.002

        self.base_quote_fee = 0.002  # 设定手续费比例
        self.base_mid_fee = 0.002
        self.quote_mid_fee = 0.002

        self.order_ratio_base_quote = 0.5  # 设定吃单比例
        self.order_ratio_base_mid = 0.5

        # 设定监控时间
        self.interval = interval

        # 设定市场初始 ------------现在没有接口，人工转币，保持套利市场平衡--------------

        self.base_quote_quote_reserve = 0.0    # 设定账户最少预留数量,根据你自己的初始市场情况而定, 注意： 是数量而不是比例
        self.base_quote_base_reserve = 0.0
        self.quote_mid_mid_reserve = 0.0
        self.quote_mid_quote_reserve = 0.0
        self.base_mid_base_reserve = 0.0
        self.base_mid_mid_reserve = 0.0

        # 最小的交易单位设定
        self.min_trade_unit = 0.2   # LTC/BTC交易对，设置为0.2, ETH/BTC交易对，设置为0.02

        self.market_price_tick = dict()  # 记录触发套利的条件时的当前行情

    def strategy(self):   # 主策略
        # 检查是否有套利空间
        try:
            # 初始化为火币市场
            huobi_market = marketHelper.Market()
            self.market_price_tick = dict()
            
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)] = \
                huobi_market.market_detail(self.base_cur, self.quote_cur)
            market_price_sell_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
            market_price_buy_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][0]
            
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)] = \
                huobi_market.market_detail(self.base_cur, self.mid_cur)
            base_mid_price_buy_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("bids")[0][0]
            base_mid_price_sell_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("asks")[0][0]
            
            self.market_price_tick["{0}_{1}".format(self.quote_cur, self.mid_cur)] = \
                huobi_market.market_detail(self.quote_cur, self.mid_cur)
            quote_mid_price_sell_1 = \
                self.market_price_tick["{0}_{1}".format(self.quote_cur, self.mid_cur)].get("asks")[0][0]
            quote_mid_price_buy_1 = \
                self.market_price_tick["{0}_{1}".format(self.quote_cur, self.mid_cur)].get("bids")[0][0]
            # 检查正循环套利
            '''
                三角套利的基本思路是，用两个市场（比如BTC/CNY，LTC/CNY）的价格（分别记为P1，P2），
                计算出一个公允的LTC/BTC价格（P2/P1），如果该公允价格跟实际的LTC/BTC市场价格（记为P3）不一致，
                就产生了套利机会
                
                对应的套利条件就是：
                ltc_cny_buy_1_price >
                btc_cny_sell_1_price*ltc_btc_sell_1_price*(1+btc_cny_slippage)*(1+ltc_btc_slippage) 
                /[(1-btc_cny_fee)*(1-ltc_btc_fee)*(1-ltc_cny_fee)*(1-ltc_cny_slippage)]
                考虑到各市场费率都在千分之几的水平，做精度取舍后，该不等式可以进一步化简成：
                (ltc_cny_buy_1_price/btc_cny_sell_1_price-ltc_btc_sell_1_price)/ltc_btc_sell_1_price
                >btc_cny_slippage+ltc_btc_slippage+ltc_cny_slippage+btc_cny_fee+ltc_cny_fee+ltc_btc_fee
                基本意思就是：只有当公允价和市场价的价差比例大于所有市场的费率总和再加上滑点总和时，做三角套利才是盈利的。
            '''
            logger.info("正循环差价：{0},滑点+手续费:{1}".format(
                (base_mid_price_buy_1 / quote_mid_price_sell_1 - market_price_sell_1)/market_price_sell_1,
                self.sum_slippage_fee())
                  )
            logger.info("逆循环差价：{0},滑点+手续费:{1}".format(
                  (market_price_buy_1 - base_mid_price_sell_1 / quote_mid_price_buy_1)/market_price_buy_1,
                   self.sum_slippage_fee())
                  )
            if (base_mid_price_buy_1 / quote_mid_price_sell_1 - market_price_sell_1)/market_price_sell_1 > \
                    self.sum_slippage_fee():
                market_buy_size = self.get_market_buy_size(huobi_market)
                market_buy_size = downRound(market_buy_size, 2)
                if market_buy_size >= self.min_trade_unit:
                    self.pos_cycle(huobi_market, market_buy_size)
                else:
                    logger.info("小于最小交易单位")

            # 检查逆循环套利

            elif (market_price_buy_1 - base_mid_price_sell_1 / quote_mid_price_buy_1)/market_price_buy_1 > \
                    self.sum_slippage_fee():
                market_sell_size = self.get_market_sell_size(huobi_market)
                market_sell_size = downRound(market_sell_size, 2)
                if market_sell_size >= self.min_trade_unit:
                    self.neg_cycle(huobi_market, market_sell_size)
                else:
                    logger.info("小于最小交易单位")
        except:
            logger.error(traceback.format_exc())

    def sum_slippage_fee(self):
        return self.base_quote_slippage + self.base_mid_slippage + self.quote_mid_slippage + \
               self.base_quote_fee + self.base_mid_fee + self.quote_mid_fee

    @staticmethod
    def get_market_name(base, quote):
        if base == "cny":
            return "{0}_{1}".format(quote, base)
        elif quote == "cny":
            return "{0}_{1}".format(base, quote)
        elif base == "btc":
            return "{0}_{1}".format(quote, base)
        else:
            return "{0}_{1}".format(base, quote)

    # 计算最保险的下单数量
    '''
        1.	LTC/BTC卖方盘口吃单数量：ltc_btc_sell1_quantity*order_ratio_ltc_btc，其中ltc_btc_sell1_quantity 代表LTC/BTC卖一档的数量，
            order_ratio_ltc_btc代表本策略在LTC/BTC盘口的吃单比例
        2.	LTC/CNY买方盘口吃单数量：ltc_cny_buy1_quantity*order_ratio_ltc_cny，其中order_ratio_ltc_cny代表本策略在LTC/CNY盘口的吃单比例
        3.	LTC/BTC账户中可以用来买LTC的BTC额度及可以置换的LTC个数：
            btc_available - btc_reserve，可以置换成
            (btc_available – btc_reserve)/ltc_btc_sell1_price个LTC
            其中，btc_available表示该账户中可用的BTC数量，btc_reserve表示该账户中应该最少预留的BTC数量
            （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
        4.	BTC/CNY账户中可以用来买BTC的CNY额度及可以置换的BTC个数和对应的LTC个数：
            cny_available - cny_reserve, 可以置换成
            (cny_available-cny_reserve)/btc_cny_sell1_price个BTC，
            相当于
            (cny_available-cny_reserve)/btc_cny_sell1_price/ltc_btc_sell1_price
            个LTC
            其中：cny_available表示该账户中可用的人民币数量，cny_reserve表示该账户中应该最少预留的人民币数量
            （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
        5.	LTC/CNY账户中可以用来卖的LTC额度：
            ltc_available – ltc_reserve
            其中，ltc_available表示该账户中可用的LTC数量，ltc_reserve表示该账户中应该最少预留的LTC数量
            （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
    '''
    def get_market_buy_size(self, huobi_market):
        market_buy_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][1] \
                          * self.order_ratio_base_quote
        base_mid_sell_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("bids")[0][1] \
                             * self.order_ratio_base_mid
        base_quote_off_reserve_buy_size = \
            (huobi_market.account_available(self.quote_cur, self.get_market_name(self.base_cur, self.quote_cur))
             - self.base_quote_quote_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
        quote_mid_off_reserve_buy_size = \
            (huobi_market.account_available(self.mid_cur, self.get_market_name(self.quote_cur, self.mid_cur)) -
             self.quote_mid_mid_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.quote_cur, self.mid_cur)].get("asks")[0][0] / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
        base_mid_off_reserve_sell_size = \
            huobi_market.account_available(self.base_cur, self.get_market_name(self.base_cur, self.mid_cur)) - \
            self.base_mid_base_reserve
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(market_buy_size, base_mid_sell_size,
                                                      base_quote_off_reserve_buy_size, quote_mid_off_reserve_buy_size,
                                                      base_mid_off_reserve_sell_size))
        return math.floor(min(market_buy_size, base_mid_sell_size, base_quote_off_reserve_buy_size,
                              quote_mid_off_reserve_buy_size, base_mid_off_reserve_sell_size)*10000)/10000

    '''
        卖出的下单保险数量计算
        假设BTC/CNY盘口流动性好
        1. LTC/BTC买方盘口吃单数量：ltc_btc_buy1_quantity*order_ratio_ltc_btc，其中ltc_btc_buy1_quantity 代表LTC/BTC买一档的数量，
           order_ratio_ltc_btc代表本策略在LTC/BTC盘口的吃单比例
        2. LTC/CNY卖方盘口卖单数量：ltc_cny_sell1_quantity*order_ratio_ltc_cny，其中order_ratio_ltc_cny代表本策略在LTC/CNY盘口的吃单比例
        3. LTC/BTC账户中可以用来卖LTC的数量：
           ltc_available - ltc_reserve，
           其中，ltc_available表示该账户中可用的LTC数量，ltc_reserve表示该账户中应该最少预留的LTC数量
          （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
        4.	BTC/CNY账户中可以用来卖BTC的BTC额度和对应的LTC个数：
            btc_available - btc_reserve, 可以置换成
            (btc_available-btc_reserve) / ltc_btc_sell1_price个LTC
            其中：btc_available表示该账户中可用的BTC数量，btc_reserve表示该账户中应该最少预留的BTC数量
           （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
        5.	LTC/CNY账户中可以用来卖的cny额度：
            cny_available – cny_reserve，相当于
            (cny_available – cny_reserve) / ltc_cny_sell1_price个LTC
            其中，cny_available表示该账户中可用的人民币数量，cny_reserve表示该账户中应该最少预留的人民币数量
            （这个数值由用户根据自己的风险偏好来设置，越高代表用户风险偏好越低）。
        
    '''
    def get_market_sell_size(self, huobi_market):
        market_sell_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][1] \
                           * self.order_ratio_base_quote
        base_mid_buy_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("asks")[0][1] \
                            * self.order_ratio_base_mid
        base_quote_off_reserve_sell_size = \
            huobi_market.account_available(self.base_cur, self.get_market_name(self.base_cur, self.quote_cur)) \
            - self.base_quote_base_reserve
        quote_mid_off_reserve_sell_size = \
            (huobi_market.account_available(self.quote_cur, self.get_market_name(self.quote_cur, self.mid_cur)) -
             self.quote_mid_quote_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][0]
        base_mid_off_reserve_buy_size = \
            (huobi_market.account_available(self.mid_cur, self.get_market_name(self.base_cur, self.mid_cur)) -
             self.base_mid_mid_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("asks")[0][0]
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(market_sell_size, base_mid_buy_size,
                    base_quote_off_reserve_sell_size, quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size))
        return math.floor(min(market_sell_size, base_mid_buy_size, base_quote_off_reserve_sell_size,
                          quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size) * 10000) / 10000

    '''
        正循环套利
        正循环套利的顺序如下：
        先去LTC/BTC吃单买入LTC，卖出BTC，然后根据LTC/BTC的成交量，使用多线程，
        同时在LTC/CNY和BTC/CNY市场进行对冲。LTC/CNY市场吃单卖出LTC，BTC/CNY市场吃单买入BTC。
        
    '''
    def pos_cycle(self, huobi_market, market_buy_size):
        logger.info("开始正循环套利 size:{0}".format(market_buy_size))
        # return
        order_result = huobi_market.buy(cur_market_name=self.get_market_name(self.base_cur, self.quote_cur),
                                        price=self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)]
                                        .get("asks")[0][0], amount=market_buy_size)
        logger.info("买入结果：{0}".format(order_result))
        time.sleep(0.2)
        if not huobi_market.order_normal(order_result,
                                         cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)):
            # 交易失败
            logger.info("正循环交易失败，退出套利 {0}".format(order_result))
            return
        # 获取真正成交量
        retry, already_hedged_amount = 0, 0.0
        while retry < 3:   # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
                huobi_market.cancel_order(order_result, self.get_market_name(self.base_cur, self.quote_cur))

                self.wait_for_cancel(huobi_market, order_result, self.get_market_name(self.base_cur, self.quote_cur))
            field_amount = float(huobi_market.get_order_processed_amount(
                order_result, cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)))
            logger.info("field_amount:{0}{1}".format(field_amount,already_hedged_amount))

            if field_amount-already_hedged_amount < self.min_trade_unit:
                logger.info("没有新的成功交易或者新成交数量太少")
                retry += 1
                continue

            # 开始对冲
            logger.info("开始对冲，数量：{0}".format(field_amount - already_hedged_amount))
            p1 = multiprocessing.Process(target=self.hedged_sell_cur_pair,
                                         args=(field_amount-already_hedged_amount,huobi_market,
                                               self.get_market_name(self.base_cur, self.mid_cur)))
            p1.start()

            # TODO: 这里最好直接从order_result里面获取成交的quote_cur金额，然后对冲该金额
            quote_to_be_hedged = downRound((field_amount-already_hedged_amount)
                                 * self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].
                                 get("asks")[0][0], 2)
            p2 = multiprocessing.Process(target=self.hedged_buy_cur_pair,
                                         args=(quote_to_be_hedged, huobi_market,
                                               self.get_market_name(self.quote_cur, self.mid_cur)))
            p2.start()
            p1.join()
            p2.join()
            already_hedged_amount = field_amount
            if field_amount >= market_buy_size:  # 已经完成指定目标数量的套利
                break
            retry += 1
            time.sleep(0.2)
        logger.info("完成正循环套利")

    '''
        逆循环套利
        逆循环套利的顺序如下：
        先去LTC/BTC吃单卖出LTC，买入BTC，然后根据LTC/BTC的成交量，使用多线程，
        同时在LTC/CNY和BTC/CNY市场进行对冲。
        LTC/CNY市场吃单买入LTC，BTC/CNY市场吃单卖出BTC。
        
    '''
    def neg_cycle(self, huobi_market, market_sell_size):
        logger.info("开始逆循环套利")
        # return
        order_result = huobi_market.sell(cur_market_name=self.get_market_name(self.base_cur, self.quote_cur),
                                         price=self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].
                                         get("bids")[0][0], amount=market_sell_size)
        if not huobi_market.order_normal(order_result,
                                         cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)):
            # 交易失败
            logger.info("逆循环交易失败，退出套利 {0}".format(order_result))
            return
        time.sleep(0.2)
        # 获取真正成交量
        retry, already_hedged_amount = 0, 0.0
        while retry < 3:  # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
                huobi_market.cancel_order(order_result, self.get_market_name(self.base_cur, self.quote_cur))

                self.wait_for_cancel(huobi_market, order_result, self.get_market_name(self.base_cur, self.quote_cur))

            field_amount = float(huobi_market.get_order_processed_amount(
                    order_result, cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)))
            logger.info("field_amount:{0}{1}".format(field_amount, already_hedged_amount))

            if field_amount - already_hedged_amount < self.min_trade_unit:
                logger.info("没有新的成功交易或者新成交数量太少")
                retry += 1
                continue

            # 开始对冲
            logger.info("开始对冲，数量：{0}".format(field_amount - already_hedged_amount))
            p1 = multiprocessing.Process(target=self.hedged_buy_cur_pair,
                                         args=(field_amount - already_hedged_amount, huobi_market,
                                               self.get_market_name(self.base_cur, self.mid_cur)))
            p1.start()

            # TODO: 这里最好直接从order_result里面获取成交的quote_cur金额，然后对冲该金额
            quote_to_be_hedged = downRound((field_amount - already_hedged_amount) *
                                 self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].
                                 get("bids")[0][0], 2)
            p2 = multiprocessing.Process(target=self.hedged_sell_cur_pair,
                                         args=(quote_to_be_hedged, huobi_market,
                                               self.get_market_name(self.quote_cur, self.mid_cur)))
            p2.start()
            p1.join()
            p2.join()
            already_hedged_amount = field_amount
            if field_amount >= market_sell_size:  # 已经完成指定目标数量的套利
                break
            retry += 1
            time.sleep(0.2)
        logger.info("结束逆循环套利")

    def hedged_buy_cur_pair(self, buy_size, huobi_market, cur_pair):
        """
        对冲买入货币对
        :param buy_size: 买入数量
        :param huobi_market: 火币市场实例
        :param cur_pair: 货币对名称
        :return:
        """
        logger.info("开始买入{0}".format(cur_pair))
        try:
            order_result = huobi_market.buy(cur_market_name=cur_pair,
                                            price=self.market_price_tick["{0}".format(cur_pair)].
                                            get("asks")[0][0], amount=downRound(buy_size, 2))
            hedged_amount = 0.0
            time.sleep(0.2)
            logger.info("买入结果：{0}".format(order_result))
            if huobi_market.order_normal(order_result,
                                         cur_market_name=cur_pair):
                huobi_market.cancel_order(order_result, cur_pair)  # 取消未成交的order

                self.wait_for_cancel(huobi_market, order_result, cur_pair)
                hedged_amount = float(huobi_market.get_order_processed_amount(
                    order_result, cur_market_name=cur_pair))
            else:
                # 交易失败
                logger.info("买入{0} 交易失败 {1}".format(cur_pair, order_result))
            if buy_size > hedged_amount:
                # 对未成交的进行市价交易
                buy_amount = self.market_price_tick["{0}".format(cur_pair)].get("asks")[4][0] \
                             * (buy_size - hedged_amount)  # 市价的amount按5档最差情况预估
                buy_amount = max(HUOBI_BTC_MIN_ORDER_CASH, buy_amount)
                market_order_result = huobi_market.buy_market(cur_market_name=cur_pair, amount=downRound(buy_amount, 2))
                logger.info(market_order_result)
        except:
            logger.error(traceback.format_exc())
        logger.info("结束买入{0}".format(cur_pair))

    def hedged_sell_cur_pair(self, sell_size, huobi_market, cur_pair):
        """
        对冲卖出货币对
        :param sell_size: 卖出头寸
        :param huobi_market: 火币市场实例
        :param cur_pair: 货币对名称
        :return:
        """
        logger.info("开始卖出{0}".format(cur_pair))
        try:
            order_result = huobi_market.sell(cur_market_name=cur_pair,
                                             price=self.market_price_tick["{0}".format(cur_pair)].get("bids")[0][0],
                                             amount=sell_size)
            hedged_amount = 0.0
            time.sleep(0.2)
            logger.info("卖出结果：{0}".format(order_result))
            if huobi_market.order_normal(order_result,
                                         cur_market_name=cur_pair):
                huobi_market.cancel_order(order_result, cur_pair)
                self.wait_for_cancel(huobi_market, order_result, cur_pair)

                hedged_amount = float(huobi_market.get_order_processed_amount(order_result, cur_market_name=cur_pair))
            else:
                # 交易失败
                logger.info("卖出{0} 交易失败  {1}".format(cur_pair, order_result))

            if sell_size > hedged_amount:
                # 对未成交的进行市价交易
                sell_qty = sell_size - hedged_amount
                ccy_to_sell = cur_pair.split("_")[0]
                if ccy_to_sell == "btc":
                    sell_qty = max(HUOBI_BTC_MIN_ORDER_QTY, sell_qty)
                elif ccy_to_sell == "ltc":
                    sell_qty = max(HUOBI_LTC_MIN_ORDER_QTY, sell_qty)
                elif ccy_to_sell == "eth":
                    sell_qty = max(BITEX_ETH_MIN_ORDER_QTY, sell_qty)
                else:
                    sell_qty = max(BITEX_ETH_MIN_ORDER_QTY, sell_qty)

                market_order_result = huobi_market.sell_market(
                    cur_market_name=cur_pair,
                    amount=downRound(sell_qty, 3))
                logger.info(market_order_result)
        except:
            logger.error(traceback.format_exc())
        logger.info("结束卖出{0}".format(cur_pair))

    @staticmethod
    def wait_for_cancel(huobi_market, order_result, market_name):
        """
        等待order  cancel完成
        :param huobi_market: 火币市场实例
        :param order_result: 订单号
        :param market_name: 货币对市场名称
        :return:
        """
        while huobi_market.get_order_status(order_result, market_name) \
                not in [2, 3, 6, "partial-canceled", "filled", "canceled"]:    # 订单完成或者取消或者部分取消
            time.sleep(0.1)

if __name__ == "__main__":
    triangle = Triangle()
    while True:
        triangle.strategy()
        time.sleep(triangle.interval)
