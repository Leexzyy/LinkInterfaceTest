# -*- coding: utf-8 -*-
# @Time    : 2024/1/3 14:20
# @Author  : Leexzyy
# @Site    : 
# @File    : create_order_and_payment.py
# @Software: PyCharm

from services.mini.create_payment import create_poly_payment
from services.mini.submit_order import submit_common_order


class CreateOrderAndPayment():
    def create_offline_order_and_payment(store_id=None, object_id=None):
        return_data = {}
        order = submit_common_order.CommonOrder().common_order(store_id=store_id, object_id=object_id)
        order_id = order['result']['data']['objectId']
        return_data['order_id'] = order_id
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=order_id)
        order_no = poly_payment['result']['data']['charge']['orderNo']
        return_data['order_no'] = order_no
        return return_data

