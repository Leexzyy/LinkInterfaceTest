# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 17:47
# @Author  : Leexzyy
# @Site    : 
# @File    : pay_result_by_order_no.py
# @Software: PyCharm
from common import config
from services import bash_api
# import bash_api
from utils import my_utils

url = 'fetchPayResultByOrderNo'


class PayResultByOrderNo(bash_api.BashApi):
    # def pay_result_by_order_no(self, order_no):
    #     json = {'orderNo': order_no}
    #     api = self.bash_request(url=url, json=json)
    #     return api

    def get_order_status_by_order_no(self, order_no):
        json_data = {'orderNo': order_no}
        api = self.bash_request(url=url, json=json_data)
        return api['result']['data']['status']
