# -*- coding: utf-8 -*-
# @Time    : 2024/1/10 16:32
# @Author  : Leexzyy
# @Site    : 
# @File    : order_after_sales.py
# @Software: PyCharm
from common import config
from services import bash_api

url = 'fetchOrderAfterSales'


class OrderAfterSalesAPI(bash_api.BashApi):
    def order_after_sales(self, order_id):
        json_data = {
            'orderId': order_id,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        api = self.bash_request(url=url, json=json_data)
        return api['result']['data']['aduit']['status']
