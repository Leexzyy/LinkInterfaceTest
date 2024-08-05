from services import bash_api

url = 'updateOrder'


class updataOrderAPI(bash_api.BashApi):

    def updata_order(self, order_id):
        json_data = {"objectId": f'{order_id}', "attrs": {"thirdOrderId": "auto_test_mock"}}
        response = self.bash_request(
            url=url,
            json=json_data,
        )
        return response
