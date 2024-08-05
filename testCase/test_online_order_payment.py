# -*- coding: utf-8 -*-
# @Time    : 2024/1/9 16:20
# @Author  : Leexzyy
# @Site    :
# @File    : test_online_order_payment.py
# @Software: PyCharm
import time
import unittest
# from threading import Thread
import concurrent.futures

from services.mini.refund_order import apply_after_sales
from services.mini.check_order_status import pay_result_by_order_no, fetch_data_by_traceId, order_after_sales, \
    common_order_detail
from services.mini.create_payment import create_poly_payment, mock_payhook
from services.mini.cancel_order import cancel_sale_activity_order
from services.admin import item_action_record
from services.mini.submit_order import submit_cash_order_async
from services.mini.polymerisation import seckill_cash_order_and_payment
from services.mongodb import updata_order
from utils import env_utils, mongod_utils, my_utils
import get_path_info


class TestOnlineOrderPayment(unittest.TestCase):
    check_test_is_build = True
    path = None
    env_tool = None
    env = None
    store_id = None
    object_id = None
    bug_model = None

    @classmethod
    def setUpClass(cls):
        cls.path = get_path_info.get_path()
        cls.env_tool = env_utils.EnvTool(f'{cls.path}/payment.env')
        cls.debug_model = cls.env_tool.get_value('DEBUG_MODEL')
        cls.env = my_utils.get_env()
        if cls.env != 'PRO':
            print('测试环境为：测试环境')
            cls.store_id = cls.env_tool.get_value('TEST_STORE_ID')
            cls.object_id = cls.env_tool.get_value('TEST_ONLINE_GOODS_OBJECT_ID')
        else:
            print('测试环境为：生产环境')
            cls.store_id = cls.env_tool.get_value('PRO_STORE_ID')
            cls.object_id = cls.env_tool.get_value('PRO_ONLINE_GOODS_OBJECT_ID')
        print(f'自动化测试用例中的DEBUG_MODEL为：{cls.bug_model},执行环境为：{cls.env}')

    def test_001_payment_success(self):
        """线上商城下单成功"""
        print('# 1: 调用创建订单接口创建订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        time.sleep(1)
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#4 进行mock支付操作")
        mock_payhook.MockPayHook().mock_payhook_v2(order_no, 1)
        print('# 5 获取支付结果进行断言（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')

    def test_002_online_order_manual_cancel_order(self):
        """手动取消现金支付订单"""
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("# 4:手动取消订单 （cancelSaleActivityOrder）")
        order_status = cancel_sale_activity_order.CancelSaleActivityOrder().cancel_sale_activity_order_v2(order_id)
        self.assertEqual(order_status, 'success', '手动取消订单失败')
        print('# 5:查看订单状态(fetchCommonOrderDetail)')
        order_detail_status = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_detail_status, 'canceled', '订单状态不为取消成功')

    def test_003_online_order_pay_success_and_refund(self):
        """线上支付订单付款成功后进行退款"""
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#4 进行mock支付操作")
        mock_payhook.MockPayHook().mock_payhook_v2(order_no, 1)
        print('# 5 获取支付结果进行断言（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        print('# 6 用户小程序点击退款（xxx）')
        refund_objectId = apply_after_sales.AppleAfterSalesAPI().apple_after_sales_by_cash_v2(order_id)
        print("# 7 插入数据模拟旺电通回调")
        updata_order.updataOrderAPI().updata_order(order_id)
        print('# 8 admin点击退款')
        refund_status = item_action_record.Item_Action_Record().item_action_record_online_refund(refund_objectId)
        self.assertEqual('approved', refund_status, '订单退款后状态验证失败')
        print('# 9 通过订单号查询订单详情（data_by_trace_id）')
        order_status = order_after_sales.OrderAfterSalesAPI().order_after_sales(order_id)
        self.assertEqual('approved', order_status, '订单退款后状态验证失败')

    @unittest.skipIf(check_test_is_build, '跳过测试')
    def test_004_online_order_auto_cancel_order(self):
        """线上支付订单付款成功后自动取消订单"""
        session_id = my_utils.get_uuid()
        order_data = seckill_cash_order_and_payment.SeckillCashOrderAndPayment().seckill_cash_order_and_payment(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        time.sleep(15 * 60)
        # 4 查看订单状态是否为已关闭
        print('# 4 查看订单状态是否为已关闭')
        order_detail = common_order_detail.CommonOrderDetail().common_order_v2(order_data['order_id'])
        print(order_detail)
        order_status = order_detail['result']['data']['order']['status']
        self.assertEqual('closed', order_status, '订单状态不为已取消')

    def test_005_enter_wrong_channel(self):
        """输入错误的渠道 系统是否进行处理"""
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment_json_data = {
            'sessionId': my_utils.get_uuid(),
            "channel": "xxx", "tradeType": "payment",
            "subject": "您已购买的门店商品", "body": "您已购买的门店商品",
            "__platform": "mini", "__envVersion": "develop",
            "orderIds": '',
        }
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment(poly_payment_json_data)
        self.assertEqual(poly_payment['result']['error']['message'], '不支持该支付渠道', '渠道断言错误')

    def test_006_concurrent_payment(self):
        """并发调用下单接口"""

        def create_poly(order=None, session_id=None):
            poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_session_id_fixed(orderId=order,
                                                                                                        amount=1,
                                                                                                        session_id=session_id)
            return poly_payment

        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        session_id = my_utils.get_uuid()
        # poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 2 获取支付参数（_createPolyPayment）')
            future1 = executor.submit(create_poly, order_id, session_id)
            future2 = executor.submit(create_poly, order_id, session_id)
            # 获取线程函数的返回内容
            result1 = future1.result()
            result2 = future2.result()
            print(f"result1 = {result1}")
            print(f"result2 = {result2}")
            try:
                if result1['result']['data']['charge']['orderNo'] is not None and result2['result']['data']['charge'][
                    'orderNo'] is not None:
                    raise Exception('订单重复生成')
            except Exception as e:
                self.assertEqual("'data'", str(e), '订单重复生成系统未进行处理')

    def test_007_storeId_not_exist(self):
        """线上商城storedID不存在时"""
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        error_store_id = self.store_id[0:-1]
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=error_store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data']['error']['message'], '未配置库存',
                         'order_id未配置时有误')
        self.assertEqual(order_detail['result']['data']['data']['error']['name'], 'CloudError', 'order_id未配置时有误')
        self.assertEqual(order_detail['result']['data']['data']['error']['status'], 400, 'order_id未配置时有误')

    def test_008_concurrent_SubmitCashOrderAsyncAPI(self):
        """线上商城并发创建订单"""
        session_id = my_utils.get_uuid()

        def create_order(my_session_id):
            cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
                store_id=self.store_id, object_id=self.object_id, qty=1, session_id=my_session_id)
            return cash_order

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 1 并发创建订单')
            future1 = executor.submit(create_order, session_id)
            future2 = executor.submit(create_order, session_id)
            # 获取线程函数的返回内容
            result1 = future1.result()
            result2 = future2.result()
            print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
            order_detail1 = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(
                result1['result']['data']['traceId'])
            order_detail2 = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(
                result2['result']['data']['traceId'])
            print(order_detail1)
            print(order_detail2)
            try:
                message1 = order_detail1['result']['data']['data'][0]
                message2 = order_detail1['result']['data']['data'][0]
                self.assertIsNotNone(message1)
                self.assertIsNotNone(message2)
                raise Exception('订单重复生成', result1)
            except Exception as e:
                print('订单未进行重复生成')

    def test_009_concurrent_refund_order(self):
        """订单并发取消且退款"""
        """线上支付订单付款成功后进行退款"""
        print('# 1: 调用下单接口生成订单 (submitCashOrderAsync)')
        session_id = my_utils.get_uuid()
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=session_id)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data'][0]['status'], 'created', '订单状态不为创建成功')
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("# 3:调用下单接口进行下单 （create_poly_payment）")
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_v2(order_id, 1)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        print("#4 进行mock支付操作")
        mock_payhook.MockPayHook().mock_payhook_v2(order_no, 1)
        print('# 5 获取支付结果进行断言（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        print('# 6 用户小程序点击退款（xxx）')
        refund_objectId = apply_after_sales.AppleAfterSalesAPI().apple_after_sales_by_cash_v2(order_id)
        print("# 7 插入数据模拟旺电通回调")
        updata_order.updataOrderAPI().updata_order(order_id)
        print('# 8 admin点击退款')

        def admin_refund(refund_objectId=None):
            refund_status = item_action_record.Item_Action_Record().item_action_record_online_refund(refund_objectId)
            return refund_status

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 9 并发执行退款')
            future1 = executor.submit(admin_refund, refund_objectId)
            future2 = executor.submit(admin_refund, refund_objectId)
            # 获取线程函数的返回内容
            result1 = future1.result()
            result2 = future2.result()
            print(f"result1 = {result1}")
            print(f"result2 = {result2}")
        # self.assertEqual('approved', refund_status, '订单退款后状态验证失败')
        # print('# 9 通过订单号查询订单详情（data_by_trace_id）')
        # order_status = order_after_sales.OrderAfterSalesAPI().order_after_sales(order_id)
        # self.assertEqual('approved', order_status, '订单退款后状态验证失败')

    def test_010_submitCashOrderAsync_session_id_is_null(self):
        """现金支付时session_id为空验证"""
        print('# 1: 调用创建订单接口创建订单 (submitCashOrderAsync)')
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_v2(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=None)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data']['error']['status'], 400, '订单状态异常')
        self.assertEqual(order_detail['result']['data']['data']['error']['message'], '需要传递参数: sessionId',
                         '接口返回参数异常')

    def test_011_submitCashOrderAsync_session_id_is_none(self):
        """现金支付时不传session_id验证"""
        print('# 1: 调用创建订单接口创建订单 (submitCashOrderAsync)')
        cash_order = submit_cash_order_async.SubmitCashOrderAsyncAPI().submit_cash_order_async_session_id_null(
            store_id=self.store_id, object_id=self.object_id, qty=1, session_id=None)
        self.assertIsNotNone(cash_order['result']['data']['traceId'], '生成traceId失败')
        traceid = cash_order['result']['data']['traceId']
        print("# 2: 调用查询接口查询订单详情（data_by_trace_id）")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(order_detail['result']['data']['data']['error']['status'], 400, '订单状态异常')
        self.assertEqual(order_detail['result']['data']['data']['error']['message'], '需要传递参数: sessionId',
                         '接口返回参数异常')


if __name__ == '__main__':
    unittest.main()
