# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 18:10
# @Author  : Leexzyy
# @Site    : 
# @File    : cancel_after_sales.py
# @Software: PyCharm
from common import config
from services import bash_api
from utils import my_utils

url = 'cancelAfterSales'


class cancelAfterSalesAPI(bash_api.BashApi):

    def cancel_after_sales(self, order_id):
        json_data = {
            'sessionId':my_utils.get_uuid(),
            'afterSalesId': order_id,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        response = self.bash_request(
            url=url,
            json=json_data,
        )
        return response['result']['data']['aduit']['status']
