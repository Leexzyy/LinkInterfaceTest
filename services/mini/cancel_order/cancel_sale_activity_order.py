# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 17:51
# @Author  : Leexzyy
# @Site    : 
# @File    : cancel_sale_activity_order.py
# @Software: PyCharm
from common import config
from services import bash_api
# import bash_api
from utils import my_utils

url = 'cancelSaleActivityOrder'


class CancelSaleActivityOrder(bash_api.BashApi):
    def cancel_sale_activity_order(self, order_id):
        json = {'orderId': order_id}
        api = self.bash_request(url=url, json=json)
        return api


    def cancel_sale_activity_order_v2(self, order_id):
        json = {'orderId': order_id}
        api = self.bash_request(url=url, json=json)
        return api['result']['data']['status']
