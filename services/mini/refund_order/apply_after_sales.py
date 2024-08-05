import requests
from common import config
from services import bash_api
from utils import my_utils

url = 'applyAfterSales'


class AppleAfterSalesAPI(bash_api.BashApi):

    def apple_after_sales(self, json):
        response = self.bash_request(
            url=url,
            json=json,
        )
        return response

    def apple_after_sales_by_cash_v2(self, order_id):
        json_data = {
            'sessionId': my_utils.get_uuid(),
            'type': '1',
            'reason': '7天无理由退换货',
            'remark': '',
            'goodsImgs': [],
            'goodsStatus': '未收到货',
            'payType': 'cash',
            'orderId': order_id,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        response = self.bash_request(
            url=url,
            json=json_data,
        )
        return response['result']['data']['objectId']

    def apple_after_sales_by_point_v2(self, order_id):
        json_data = {
            'sessionId': my_utils.get_uuid(),
            'type': '1',
            'reason': '7天无理由退换货',
            'remark': '',
            'goodsImgs': [],
            'goodsStatus': '未收到货',
            'payType': 'point',
            'orderId': order_id,
            '__platform': 'mini',
            '__envVersion': 'develop',
        }
        response = self.bash_request(
            url=url,
            json=json_data,
        )
        return response['result']['data']['objectId']
