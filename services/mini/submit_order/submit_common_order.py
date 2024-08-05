# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 14:25
# @Author  : Leexzyy
# @Site    : 创建订单
# @File    : submit_common_order.py
# @Software: PyCharm
from common import config
from services import bash_api
# import bash_api
from utils import my_utils

url = 'submitCommonOrder'


class CommonOrder(bash_api.BashApi):

    def common_order(self, status_code=config.STATUS_CODE, store_id=None, object_id=None,
                     session_id=None):
        if session_id is None:
            json = {
                'subType': 'selfhelp',
                'isFromCart': True,
                'remark': '',
                'sessionId': my_utils.get_uuid(),
                'cart': {
                    'storeId': store_id,
                    'deliveryFee': 0,
                    'items': [
                        {
                            'qty': 1,
                            'objectId': object_id,
                            'features': [
                                {
                                    'qty': 1,
                                    'propertyList': [
                                        {
                                            'name': '标准',
                                            'title': '温度',
                                            'code': '101',
                                            'titleCode': 'WD001',
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                    'ingredientsList': [],
                },
                'templateSortedList': [],
                'shipAddress': {
                    'userName': '微信用户',
                    'telNumber': '18597940021',
                },
                '__platform': 'mini',
                '__envVersion': 'develop',
            }
            api = self.bash_request(url=url, json=json, status_code=status_code, timeout=0.4)
            return api
        else:
            json = {
                'subType': 'selfhelp',
                'isFromCart': True,
                'remark': '',
                'sessionId': session_id,
                'cart': {
                    'storeId': store_id,
                    'deliveryFee': 0,
                    'items': [
                        {
                            'qty': 1,
                            'objectId': object_id,
                            'features': [
                                {
                                    'qty': 1,
                                    'propertyList': [
                                        {
                                            'name': '标准',
                                            'title': '温度',
                                            'code': '101',
                                            'titleCode': 'WD001',
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                    'ingredientsList': [],
                },
                'templateSortedList': [],
                'shipAddress': {
                    'userName': '微信用户',
                    'telNumber': '18597940021',
                },
                '__platform': 'mini',
                '__envVersion': 'develop',
            }
            api = self.bash_request(url=url, json=json, status_code=status_code, timeout=0.4)
            return api
