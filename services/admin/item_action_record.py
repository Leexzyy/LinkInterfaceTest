# -*- coding: utf-8 -*-
# @Time    : 2023/12/22 12:28
# @Author  : Leexzyy
# @Site    : ADMIN端退款接口
# @File    : item_action_record.py
# @Software: PyCharm
import time

from common import config
from services import bash_api
from userInfo import user_info

url = 'itemActionRecord'


class Item_Action_Record(bash_api.BashApi):
    def item_action_record(self, order_id):
        time.sleep(3)
        json = {
            'funcName': 'cancelOrder',
            'params': {
                'orderId': order_id,
            },
        }
        response = self.admin_api(
            url=url,
            json=json,
        )
        return response

    def item_action_record_online_refund(self, object_id):
        json = {
            'funcName': 'auditAfterSales',
            'params': {
                'aduit': {
                    'refuseRease': 'test.py',
                    'status': 'approved',
                },
                'objectId': object_id,
            },
        }
        response = self.admin_api(
            url=url,
            json=json,
            timeout=5
        )
        return response['result']['data']['aduit']['status']


    def user_add_energy(self, enegry_num):
        user_id = user_info.get_user_id()
        json_data = {
            'funcName': 'adminManageEnergy',
            'params': {
                'energy': enegry_num,
                'userId': user_id,
                'manageType': 'add',
                "remark": "自动化测试初始化用户能量 - 增加能量"
            }
        }
        response = self.admin_api(
            url=url,
            json=json_data,
            timeout=5
        )
        return response

    def user_remove_energy(self, enegry_num):
        user_id = user_info.get_user_id()
        json = {"funcName": "adminManageEnergy",
                "params": {
                    "energy": enegry_num,
                    "remark": "自动化测试初始化用户能量-扣除能量",
                    "userId": user_id,
                    "manageType": "deduct"}}
        response = self.admin_api(
            url=url,
            json=json,
            timeout=5
        )
        return response


if __name__ == '__main__':
    pass
