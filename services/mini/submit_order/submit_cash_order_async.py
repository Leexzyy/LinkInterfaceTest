# -*- coding: utf-8 -*-
# @Time    : 2024/1/9 15:42
# @Author  : Leexzyy
# @Site    : 
# @File    : seckill.py
# @Software: PyCharm
import requests
from common import config
from services import bash_api
from utils import my_utils

url = 'submitCashOrderAsync'


class SubmitCashOrderAsyncAPI(bash_api.BashApi):

    def submit_cash_order_async(self, json):
        response = self.bash_request(
            url=url,
            json=json,
        )
        return response

    def submit_cash_order_async_v2(self, store_id, object_id, qty, session_id):
        if session_id is None:  # session id为空时
            submit_cash_order_data = {
                'traceId': my_utils.get_uuid(),
                'sessionId': '',
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
                'usePointDeduction': 'true',
                # 'funcName': 'submitCashOrderAsync',
                '__platform': 'mini',
                '__envVersion': 'develop',
            }
        else:  # session_id 自己传入时（并发测试的条件）
            submit_cash_order_data = {
                'traceId': my_utils.get_uuid(),
                'sessionId': session_id,
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
                'usePointDeduction': 'true',
                # 'funcName': 'submitCashOrderAsync',
                '__platform': 'mini',
                '__envVersion': 'develop',
            }

        response = self.bash_request(
            url=url,
            json=submit_cash_order_data,
        )
        return response

    def submit_cash_order_async_session_id_null(self, store_id, object_id, qty, session_id):
        submit_cash_order_data = {
            'traceId': my_utils.get_uuid(),
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
            'usePointDeduction': True,
            # 'funcName': 'submitCashOrderAsync',
            '__platform': 'mini',
            '__envVersion': 'develop',
        }

        response = self.bash_request(
            url=url,
            json=submit_cash_order_data,
        )
        return response
