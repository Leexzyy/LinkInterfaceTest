# -*- coding: utf-8 -*-
# @Time    : 2024/1/9 15:42
# @Author  : Leexzyy
# @Site    : 
# @File    : seckill.py
# @Software: PyCharm
import time

import requests
from common import config
from services import bash_api
from utils import my_utils

url = 'submitPointOrderAsync'


class SubmitPointOrderAsyncAPI(bash_api.BashApi):

    def point_order(self, store_id, object_id, qty):
        submit_cash_order_data = {
            'traceId': my_utils.get_uuid(),
            'sessionId': my_utils.get_uuid(),
            'productList': [
                {
                    'storeId': store_id,
                    'items': [
                        {
                            'objectId': object_id,
                            'qty': qty,
                        },
                    ],
                },
            ],
            'templateSortedList': [],
            'shipAddress': {
                'detailInfo': '新港中路397号',
                'userName': '张三',
                'telNumber': '020-81167888',
                'province': '广东省',
                'city': '广州市',
                'district': '海珠区',
            },
            # 'funcName': 'submitPointOrderAsync',
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        time.sleep(1)
        response = self.bash_request(
            url=url,
            json=submit_cash_order_data,
        )
        return response

    def seckill_point_and_cash_order(self, store_id, object_id, qty, point, cash):
        submit_cash_order_data = {
            'traceId': my_utils.get_uuid(),
            'sessionId': my_utils.get_uuid(),
            'productList': [
                {
                    'storeId': store_id,
                    'items': [
                        {
                            'objectId': object_id,
                            'qty': qty,
                            'priceExtra': [
                                {
                                    'combinedPrice': [
                                        {
                                            'payType': 'point',
                                            'amount': point,
                                        },
                                        {
                                            'payType': 'cash',
                                            'amount': cash,
                                        },
                                    ],
                                    'qty': qty,
                                },
                            ],
                        },
                    ],
                },
            ],
            'templateSortedList': [],
            'shipAddress': {
                'detailInfo': '新港中路397号',
                'userName': '张三',
                'telNumber': '020-81167888',
                'province': '广东省',
                'city': '广州市',
                'district': '海珠区',
            },
            # 'funcName': 'submitPointOrderAsync',
            '__platform': 'mini',
            '__envVersion': 'develop',
        }

        response = self.bash_request(
            url=url,
            json=submit_cash_order_data,
        )
        return response
