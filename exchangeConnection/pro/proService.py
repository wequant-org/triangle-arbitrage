#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import hashlib
from urllib.parse import quote

from exchangeConnection.pro import token_api
from exchangeConnection.pro import key_api
import accountConfig

TOKEN_UPDATE_TIME = 600  # 提前此时间更新token


class ProService(object):
    def __init__(self):
        self._login_name = None
        self._pwd = None
        self._asset_pwd = None
        self._auth_data = None
        self._token = None
        self._token_expire_time = None
        self._user_id = None
        self._spot_acct_id = None

    def set_token(self, token):
        self._token = token

    def set_login_name(self, login_name):
        self._login_name = login_name

    def md5_encryption(self, pwd):
        md5 = hashlib.md5()
        md5.update((pwd + 'hello, moto').encode('utf-8'))
        return md5.hexdigest()

    def set_pwd(self, pwd, need_encryption=False):
        if need_encryption:
            self._pwd = self.md5_encryption(pwd)
        else:
            self._pwd = pwd

    def set_asset_pwd(self, asset_pwd, need_encryption=False):
        if need_encryption:
            self._asset_pwd = self.md5_encryption(asset_pwd)
        else:
            self._asset_pwd = asset_pwd
        self._set_auth_data()

    def _set_auth_data(self):
        auth_data = quote(str({"assetPwd":self._asset_pwd}))
        self._auth_data = auth_data

    def get_token(self):
        return self._token

    @classmethod
    def request_success(cls, response_dict):
        """
        :type response_dict: dict
        :return:
        """
        if response_dict is None:
            return False
        if "status" in response_dict.keys():
            if response_dict["status"] == "ok":
                return True
        return False

    @classmethod
    def get_kline(cls, symbol, freq):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny, ethbtc, ltcbtc }
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        """
        ret = token_api.get_kline(symbol, period=freq)
        if cls.request_success(ret):
            return ret
        else:
            raise Exception("Get_kline Failed. Response: %s" % ret)

    @classmethod
    def get_depth(cls, symbol, type="step1"):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny, ethbtc, ltcbtc }
        :param type: 可选值：{ percent, step1, step2, step3, step4, step5 }
        :return:
        """
        ret = token_api.get_depth(symbol, type=type)
        return ret

    @classmethod
    def get_latest_trade(cls, symbol):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny, ethbtc, ltcbtc }
        :param type: 可选值：{ percent, step1, step2, step3, step4, step5 }
        :return:
        """
        ret = token_api.get_trade(symbol)
        return ret

    def update_token(self):
        if self.expired_token():
            self.get_new_token()

    def get_new_token(self):
        ret = self._login()
        if self.request_success(ret):
            data = ret['data']
            self._user_id = data['user-id']
            self._token = data['token']
            self._token_expire_time = data['expire-time'] / 1000
        else:
            raise Exception("Login failed. Response: %s" % ret)

    def expired_token(self):
        if self._token_expire_time:
            time_diff = self._token_expire_time - time.time()
            if time_diff > TOKEN_UPDATE_TIME:
                return False
        return True

    def _login(self):
        if any([self._login_name, self._pwd]) is None:
            raise ValueError("Login Failed: login-name and password cannot be None.")
        ret = token_api.login(self._login_name, self._pwd)
        if self.request_success(ret):
            return ret
        else:
            raise Exception("Login Failed. Response: %s" % ret)

    def get_spot_acct_id(self):
        self.update_token()
        if not self._spot_acct_id:
            ret = token_api.get_accounts_all(self._token, acct_type='spot')
            if self.request_success(ret):
                self._spot_acct_id = ret['data'][0]['id']
                return self._spot_acct_id
            else:
                raise Exception("Get Spot Account ID Failed. Response: %s" % ret)
        else:
            return self._spot_acct_id

    def get_spot_acct_info(self):
        self.update_token()
        acct_id = self.get_spot_acct_id()
        ret = token_api.get_balance(self._token, acct_id)
        return ret

    def verify_token(self):
        return token_api.verify_token(self._token)

    def get_order_info(self, order_id):
        self.update_token()
        ret = token_api.order_info(order_id, self._token)
        return ret

    def _create_order(self, symbol, price, amount, order_type, acct_id):
        self.update_token()
        ret = token_api.order(symbol, price, amount, order_type, acct_id, self._token, self._auth_data)
        return ret

    def _place_order(self, order_id):
        self.update_token()
        ret = token_api.place_order(order_id, self._token, self._auth_data)
        return ret

    def order(self, symbol, price, amount, order_type, acct_id=None):
        """
        :param order_type: ['buy-market', 'sell-market', 'buy-limit', 'sell-limit']
        """
        if not acct_id:
            acct_id = self.get_spot_acct_id()
        ret = self._create_order(symbol, price, amount, order_type, acct_id)
        if self.request_success(ret):
            order_id = ret['data']
            place_ret = self._place_order(order_id)
            return place_ret
        else:
            raise Exception('Create order failed: %s' % ret)

    def cancel_order(self, order_id):
        self.update_token()
        ret = token_api.cancel_order(order_id, self._token, self._auth_data)
        return ret

    def get_active_orders(self, symbol):
        self.update_token()
        ret = token_api.active_orders(self._token, symbol)
        return ret


class ProServiceAPIKey(object):
    def __init__(self, key_index='CNY_1'):
        self.access_key = None
        self.secret_key = None
        self.key_index = key_index
        self._spot_acct_id = None

    @classmethod
    def get_kline(cls, symbol, freq):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        """
        ret = key_api.get_kline(symbol, period=freq)
        if cls.request_success(ret):
            return ret
        else:
            raise Exception("Get_kline Failed. Response: %s" % ret)

    @classmethod
    def get_depth(cls, symbol, type='step0'):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
        :param type: 可选值：{ percent, step1, step2, step3, step4, step5 }
        :return:
        """
        ret = key_api.get_depth(symbol, type=type)
        return ret

    @classmethod
    def get_latest_trade(cls, symbol):
        """
        :param symbol: 可选值：{ btccny, ltccny, btcusd, ethcny }
        :param type: 可选值：{ percent, step1, step2, step3, step4, step5 }
        :return:
        """
        ret = key_api.get_trade(symbol)
        return ret

    @classmethod
    def request_success(cls, ret):
        return ProService.request_success(ret)

    def get_spot_acct_id(self):
        if not self._spot_acct_id:
            ret = key_api.get_accounts_all(key_index=self.key_index, acct_type='spot')
            if self.request_success(ret):
                self._spot_acct_id = ret['data'][0]['id']
                return self._spot_acct_id
            else:
                raise Exception("Get Spot Account ID Failed. Response: %s" % ret)
        else:
            return self._spot_acct_id

    def get_spot_acct_info(self):
        acct_id = self.get_spot_acct_id()
        ret = key_api.get_balance(acct_id, key_index=self.key_index)
        return ret

    def _create_order(self, symbol, price, amount, order_type, acct_id):
        ret = key_api.order(symbol, price, amount, order_type, acct_id, key_index=self.key_index)
        return ret

    def _place_order(self, order_id):
        ret = key_api.place_order(order_id, key_index=self.key_index)
        return ret

    def order(self, symbol, price, amount, order_type, acct_id=None):
        """
        :param order_type: ['buy-market', 'sell-market', 'buy-limit', 'sell-limit']
        """
        if not acct_id:
            acct_id = self.get_spot_acct_id()
        ret = self._create_order(symbol, price, amount, order_type, acct_id)
        if self.request_success(ret):
            order_id = ret['data']
            place_ret = self._place_order(order_id)
            return place_ret
        else:
            raise Exception('Create order failed: %s' % ret)

    def cancel_order(self, order_id):
        ret = key_api.cancel_order(order_id, key_index=self.key_index)
        return ret

    def get_active_orders(self, symbol):
        ret = key_api.active_orders(symbol, key_index=self.key_index)
        return ret

    def get_order_info(self, order_id):
        ret = key_api.order_info(order_id, key_index=self.key_index)
        return ret


def init_pro_account(key_index, api_key=True):
    if api_key:
        pro_service = ProServiceAPIKey(key_index=key_index)
        return pro_service
    else:
        pro_service = ProService()
        acct_cfg = accountConfig.PRO[key_index]
        login_name = acct_cfg['LOGIN_NAME']
        login_pwd = acct_cfg['LOGIN_PWD']
        login_asset_pwd = acct_cfg['ASSET_PWD']
        if any([login_name, login_pwd, login_asset_pwd]) is None:
            return None
        pro_service.set_login_name(login_name)
        pro_service.set_pwd(login_pwd, True)
        pro_service.set_asset_pwd(login_asset_pwd, True)
        return pro_service