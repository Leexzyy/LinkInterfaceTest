# -*- coding: utf-8 -*-
# @Time    : 2024/1/25 10:36
# @Author  : Leexzyy
# @Site    : 
# @File    : submit_energy_order_async.py
# @Software: PyCharm
import requests
from common import config
from services import bash_api
from utils import my_utils

url = 'submitEnergyOrderAsync'


class SubmitEnergyOrderAsyncAPI(bash_api.BashApi):

    def submit_energy_order_async(self, store_id, object_id, qty):
        json_data = {
            'sessionId': my_utils.get_uuid(),
            'traceId': my_utils.get_uuid(),
            'productList': [
                {
                    'storeId': store_id,
                    'items': [
                        {
                            'qty': qty,
                            'objectId': object_id,
                            'features': [
                                {
                                    'qty': qty,
                                },
                            ],
                        },
                    ],
                },
            ],
            'shipAddress': {
                'detailInfo': '新港中路397号',
                'userName': '张三',
                'telNumber': '020-81167888',
                'province': '广东省',
                'city': '广州市',
                'district': '海珠区',
            },
            '__platform': 'mini',
            '__envVersion': 'develop',
        }

        response = self.bash_request(
            url=url,
            json=json_data,
        )
        return response
