# -*- coding: utf-8 -*-
# @Time    : 2024/1/15 10:55
# @Author  : Leexzyy
# @Site    : 
# @File    : test_point_order_payment.py
# @Software: PyCharm
import time
import unittest

from services.mini.refund_order import apply_after_sales
from services.mini.check_order_status import pay_result_by_order_no, fetch_data_by_traceId, order_after_sales, \
    common_order_detail
from services.mini.create_payment import create_poly_payment, mock_payhook
from services.mini.cancel_order import cancel_after_sales, cancel_sale_activity_order
from services.admin import item_action_record
from services.mini.submit_order import submit_point_order_async
from services.mongodb import updata_order
from userInfo import user_info
from utils import mongod_utils, my_utils


class TestPointOrderPayment(unittest.TestCase):
    store_id = None
    point_object_id = None

    @classmethod
    def setUpClass(cls):
        print("开始执行测试用例")
        # 获取执行环境
        env = my_utils.get_env()
        env_tool = my_utils.get_env_tools()
        if env != 'PRO':
            cls.store_id = env_tool.get_value('TEST_STORE_ID')
            print(f'执行环境为{env}, store_id为 {cls.store_id}')
            cls.point_object_id = env_tool.get_value('TEST_POINT_OBJECT_ID')
            print(f'point_object_id为 {cls.point_object_id}')
        else:
            cls.store_id = env_tool.get_value('PRO_STORE_ID')
            print(f'执行环境为{env}, store_id为 {cls.store_id}')
            cls.point_object_id = env_tool.get_value('PRO_POINT_OBJECT_ID')
            print(f'point_object_id {cls.point_object_id}')

    def test_001_point_payment_success(self):
        """用户纯顿点积分支付成功"""
        print("#1 获取用户使用前积分")
        user_point = user_info.get_user_point()
        point_available = user_point['point_available']
        print("#2 获取纯积分下单")
        point_order = submit_point_order_async.SubmitPointOrderAsyncAPI().point_order(self.store_id,
                                                                                      self.point_object_id,
                                                                                      1)
        self.assertIsNotNone(point_order['result']['data']['traceId'], '生成traceId失败')
        traceid = point_order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 判断订单状态")
        time.sleep(0.3)
        order_state = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_state, 'paid', '订单状态与预期不符')
        print("#5 用户积分扣除数量时候等于商品价格")
        user_point_after = user_info.get_user_point()
        point_available_after = user_point_after['point_available']
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')

    def test_002_point_order_refund(self):
        """用户纯顿点支付成功后退款"""
        print("#1 获取用户使用前积分")
        point_available = user_info.get_user_point_available()
        print("#2 获取纯积分下单")
        point_order = submit_point_order_async.SubmitPointOrderAsyncAPI().point_order(self.store_id,
                                                                                      self.point_object_id,
                                                                                      1)
        self.assertIsNotNone(point_order['result']['data']['traceId'], '生成traceId失败')
        traceid = point_order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 判断订单状态")
        time.sleep(0.3)
        # todo：循环调用♻️
        order_state = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_state, 'paid', '订单状态与预期不符')
        print("#5 用户积分扣除数量时候等于商品价格")
        point_available_after = user_info.get_user_point_available()
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')
        print("#6 用户小程序点击退款")
        refund_objectId = apply_after_sales.AppleAfterSalesAPI().apple_after_sales_by_point_v2(order_id)
        print("# 7 插入数据模拟旺电通回调")
        updata_order.updataOrderAPI().updata_order(order_id)
        print('# 8 admin点击退款')
        refund_status = item_action_record.Item_Action_Record().item_action_record_online_refund(refund_objectId)
        self.assertEqual('approved', refund_status, '订单退款后状态验证失败')
        print('# 9 通过订单号查询订单详情（order_after_sales）')
        order_status = order_after_sales.OrderAfterSalesAPI().order_after_sales(order_id)
        self.assertEqual('approved', order_status, '订单退款后状态验证失败')
        # 港哥反馈因为mock支付导致退款无法退回积分 TODO：待确认
        # print("#10 查看积分时候返还")
        # user_point_refund = user_info.get_user_point_available()
        # self.assertEqual(user_point_refund, point_available, '积分返还不正确')

    def test_003_point_order_cancel_order(self):
        """用户纯顿点创建订单后取消订单"""
        print("#1 获取用户使用前积分")
        point_available = user_info.get_user_point_available()
        print("#2 获取纯积分下单")
        point_order = submit_point_order_async.SubmitPointOrderAsyncAPI().point_order(self.store_id,
                                                                                      self.point_object_id,
                                                                                      1)
        self.assertIsNotNone(point_order['result']['data']['traceId'], '生成traceId失败')
        traceid = point_order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 判断订单状态")
        time.sleep(0.3)
        order_state = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_state, 'paid', '订单状态与预期不符')
        print("#5 用户积分扣除数量时候等于商品价格")
        point_available_after = user_info.get_user_point_available()
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')
        print("#6 用户小程序点击退款")
        refund_objectId = apply_after_sales.AppleAfterSalesAPI().apple_after_sales_by_point_v2(order_id)
        print("#7 点击取消退款")
        status = cancel_after_sales.cancelAfterSalesAPI().cancel_after_sales(refund_objectId)
        self.assertEqual('canceled', status, '订单取消后状态验证失败')
        print("#8 查看积分时候返还")
        user_point_refund = user_info.get_user_point_available()
        self.assertEqual(user_point_refund, point_available_after, '积分返还不正确')

    def test_004_point_and_cash_pay_success(self):
        """顿点和现金支付成功"""
        print("#1 获取用户使用前积分")
        point_available = user_info.get_user_point_available()
        print("#2 使用积分以及现金付款")
        order = submit_point_order_async.SubmitPointOrderAsyncAPI().seckill_point_and_cash_order(
            self.store_id,
            self.point_object_id, 1, 1, 1)
        traceid = order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 用户下单")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#5 进行mock支付操作")
        mock_payhook.MockPayHook().mock_payhook_v2(order_no, 1)
        print("#6 用户积分扣除数量时候等于商品价格")
        point_available_after = user_info.get_user_point_available()
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')
        print('# 7 获取支付结果进行断言（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')

    def test_005_point_and_cash_order_refund(self):
        """用户纯混合支付成功后退款"""
        print("#1 获取用户使用前积分")
        point_available = user_info.get_user_point_available()
        print(point_available)
        print("#2 使用积分以及现金付款")
        order = submit_point_order_async.SubmitPointOrderAsyncAPI().seckill_point_and_cash_order(
            self.store_id,
            self.point_object_id, 1, 1, 1)
        traceid = order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 用户下单")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#5 进行mock支付操作")
        # time.sleep(2)
        mock_payhook.MockPayHook().mock_payhook_v2(order_no, 1)
        print("#6 用户积分扣除数量时候等于商品价格")
        point_available_after = user_info.get_user_point_available()
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')
        print('# 7 获取支付结果进行断言（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        print("#8 用户小程序点击退款")
        refund_objectId = apply_after_sales.AppleAfterSalesAPI().apple_after_sales_by_point_v2(order_id)
        print("# 9 插入数据模拟旺电通回调")
        updata_order.updataOrderAPI().updata_order(order_id)
        print('# 10 admin点击退款')
        refund_status = item_action_record.Item_Action_Record().item_action_record_online_refund(refund_objectId)
        self.assertEqual('approved', refund_status, '订单退款后状态验证失败')
        print('# 11 通过订单号查询订单详情（data_by_trace_id）')
        order_status = order_after_sales.OrderAfterSalesAPI().order_after_sales(order_id)
        self.assertEqual('approved', order_status, '订单退款后状态验证失败')
        # 因为使用的是mock payhook 导致积分退不了 暂时不验证积分返回情况
        # print("#12 查看积分时候返还")
        # user_point_refund = user_info.get_user_point_available()
        # print(user_point_refund)
        # self.assertEqual(user_point_refund, point_available, '积分返还不正确')

    def test_006_point_and_cash_cancel_orders(self):
        """顿点和现金支付成功"""
        print("#1 获取用户使用前积分")
        point_available = user_info.get_user_point_available()
        print("#2 使用积分以及现金付款")
        order = submit_point_order_async.SubmitPointOrderAsyncAPI().seckill_point_and_cash_order(
            self.store_id,
            self.point_object_id, 1, 1, 1)
        traceid = order['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 用户下单")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#5 判断订单状态")
        time.sleep(0.3)
        order_state = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_state, 'partialPaid', '订单状态与预期不符')
        print("#6 用户积分扣除数量时候等于商品价格")
        point_available_after = user_info.get_user_point_available()
        self.assertEqual(point_available - point_available_after, 1, '用户积分扣除不正确')
        print("#7 点击取消退款")
        status = cancel_sale_activity_order.CancelSaleActivityOrder().cancel_sale_activity_order_v2(order_id)
        self.assertEqual('success', status, '订单取消后状态验证失败')
        print("#8 查看积分时候返还")
        user_point_refund = user_info.get_user_point_available()
        self.assertEqual(user_point_refund, point_available, '积分返还不正确')


if __name__ == '__main__':
    unittest.main()
