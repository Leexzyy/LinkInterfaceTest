# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 17:38
# @Author  : Leexzyy
# @Site    : 
# @File    : mock_payhook.py
# @Software: PyCharm
from common import config
from services import bash_api
# import bash_api
from utils import my_utils

url = 'payHookAsync'


class MockPayHook(bash_api.BashApi):
    def mock_payhook(self, json):
        api = self.bash_request(url=url, json=json)
        return api

    def mock_payhook_v2(self, order_no, amount):
        json_data = {
            "status": "success",
            "data": {
                "appid": "wxe53fc874ec95d052",
                "bank_type": "OTHERS",
                "cash_fee": "1",
                "fee_type": "CNY",
                "is_subscribe": "N",
                "mch_id": "1574440551",
                "nonce_str": "rt804x8d23e",
                "openid": "o2jF85U9dNPnktrKobd1EXrg7pwE",
                "out_trade_no": order_no,
                "result_code": "SUCCESS",
                "return_code": "SUCCESS",
                "sign": "40F4D9A229F7F390DD43224BC2D0A37A",
                "time_end": "20231205154215",
                "total_fee": "1",
                "trade_type": "JSAPI",
                "transaction_id": "4200002021202312056098877424",
                "orderNo": order_no,
                "transactionNo": "4200002021202312056098877424",
                "noPay": 'false',
                "amount": amount
            }
        }
        api = self.bash_request(url=url, json=json_data)
        return api
