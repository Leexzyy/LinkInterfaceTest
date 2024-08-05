# -*- coding: utf-8 -*-
# @Time    : 2024/1/9 16:54
# @Author  : Leexzyy
# @Site    : 
# @File    : fetch_data_by_traceId.py
# @Software: PyCharm
import time

import requests
from common import config
from services import bash_api

url = 'fetchDataByTraceId'


class DataByTraceIdAPI(bash_api.BashApi):

    def data_by_trace_id(self, trace_id):
        time.sleep(1)
        json = {'traceId': trace_id,
                '__platform': 'mini',
                '__envVersion': 'develop', }
        response = self.bash_request(
            url=url,
            json=json,
        )
        return response

if __name__ == '__main__':
    DataByTraceIdAPI().data_by_trace_id('92ccec7f-193d-4d93-a732-05e79e9baafb')