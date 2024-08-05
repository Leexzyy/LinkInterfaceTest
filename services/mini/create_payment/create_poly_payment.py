# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 17:02
# @Author  : Leexzyy
# @Site    : 
# @File    : create_poly_payment.py
# @Software: PyCharm
from common import config
from services import bash_api
from utils import my_utils

url = 'createPolyPayment'


class CreatePolyPayment(bash_api.BashApi):
    def create_poly_payment(self, json):
        api = self.bash_request(url=url, json=json)
        return api

    def create_poly_payment_offline(self, order_id, channel='wx_lite_native', session_id=None):
        if session_id is None:
            json = {
                'sessionId': my_utils.get_uuid(),
                "channel": channel, "tradeType": "payment",
                "subject": "您已购买的门店商品", "body": "您已购买的门店商品",
                "__platform": "mini", "__envVersion": "develop",
                "orderIds": order_id,
            }
            api = self.bash_request(url=url, json=json, timeout=10)
            return api
        else:
            json = {
                'sessionId': session_id,
                "channel": channel, "tradeType": "payment",
                "subject": "您已购买的门店商品", "body": "您已购买的门店商品",
                "__platform": "mini", "__envVersion": "develop",
                "orderIds": order_id,
            }
            api = self.bash_request(url=url, json=json, timeout=10)
            return api

    def create_poly_payment_v2(self, orderId, amount):
        json_data = {
            'channel': 'wx_lite_native',
            'tradeType': 'payment',
            'sessionId': my_utils.get_uuid(),
            'subject': '订单支付',
            'body': '订单支付',
            'orderIds': orderId,
            'amount': amount,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        api = self.bash_request(url=url, json=json_data, timeout=10)
        return api

    def create_poly_payment_session_id_fixed(self, orderId, amount, session_id):
        json_data = {
            'channel': 'wx_lite_native',
            'tradeType': 'payment',
            'sessionId': session_id,
            'subject': '订单支付',
            'body': '订单支付',
            'orderIds': orderId,
            'amount': amount,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        api = self.bash_request(url=url, json=json_data, timeout=10)
        return api
