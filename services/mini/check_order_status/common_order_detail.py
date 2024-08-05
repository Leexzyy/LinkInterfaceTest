# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 16:27
# @Author  : Leexzyy
# @Site    : 
# @File    : common_order_detail.py
# @Software: PyCharm
import time

from services import bash_api
# import bash_api

url = 'fetchCommonOrderDetail'


class CommonOrderDetail(bash_api.BashApi):
    def common_order(self, json):
        time.sleep(1)
        api = self.bash_request(url=url, json=json, timeout=0.4)
        return api

    def common_order_v2(self, order_id):
        time.sleep(1)
        json = {
            "orderId": order_id
        }
        api = self.bash_request(url=url, json=json, timeout=0.4)
        return api['result']['data']['order']['status']

    def order_detail(self, order_id):
        time.sleep(1)
        json = {
            "orderId": order_id
        }
        api = self.bash_request(url=url, json=json)
        return api


if __name__ == '__main__':
    CommonOrderDetail().common_order_v2('unKeuqhLSc13HahMr58Dahq5')
