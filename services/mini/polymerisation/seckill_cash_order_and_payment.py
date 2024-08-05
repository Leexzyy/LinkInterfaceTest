# -*- coding: utf-8 -*-
# @Time    : 2024/1/11 14:51
# @Author  : Leexzyy
# @Site    : 
# @File    : seckill_cash_order_and_payment.py
# @Software: PyCharm
from services.mini.check_order_status import fetch_data_by_traceId
from services.mini.create_payment import create_poly_payment
from services.mini.submit_order import submit_cash_order_async
from utils import my_utils


class SeckillCashOrderAndPayment():
    def seckill_cash_order_and_payment(self, store_id=None, object_id=None, qty=None):
        """
        封装秒杀接口和支付接口
        :param: self  传入unittest对象 用来获取断言内容
        """
        return_data = {}
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id,
            object_id,
            qty, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        return_data['traceid'] = traceid
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        return_data['order_id'] = order_id
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        return_data['order_no'] = poly_payment['result']['data']['charge']['orderNo']
        return return_data
