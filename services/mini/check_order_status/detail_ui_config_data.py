# -*- coding: utf-8 -*-
# @Time    : 2023/12/22 19:00
# @Author  : Leexzyy
# @Site    : ADMIN端订单查询接口
# @File    : detail_ui_config_data.py
# @Software: PyCharm
import requests
from common import config
from services import bash_api

url = 'fetchDetailUIConfigData_v2'


class DetailUIConfigData(bash_api.BashApi):
    def detail_ui_config_data_v2(self, object_id):
        json = {"objectId": object_id, "tableName": "Order", "branch": "offline",
                "pageConfig": {"items": {"pageNo": 0, "limit": 10}, "payment": {"pageNo": 0, "limit": 10},
                               "refundList": {"pageNo": 0, "limit": 10}, "pushOrderList": {"pageNo": 0, "limit": 10}}}
        response = self.bash_request(
            url=url,
            json=json)
        return response
