# -*- coding: utf-8 -*-
# @Time    : 2022/7/27 13:40
# @Author  : Leexzyy
# @Explain :
# @File    : test_offline_order_payment.py
# @Software: PyCharm
import concurrent.futures
import time
import unittest
# from threading import Thread
from time import sleep

import get_path_info
from services.admin import item_action_record
from services.mini.cancel_order import cancel_sale_activity_order
from services.mini.check_order_status import pay_result_by_order_no, detail_ui_config_data, common_order_detail
from services.mini.check_order_status.common_order_detail import CommonOrderDetail
from services.mini.create_payment import create_poly_payment, mock_payhook
from services.mini.polymerisation import create_order_and_payment
from services.mini.submit_order import submit_common_order
from utils import my_utils, env_utils


class TestOfflineOrderPayment(unittest.TestCase):
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
            cls.store_id = cls.env_tool.get_value('TEST_OFFLINE_STORE_ID')
            cls.object_id = cls.env_tool.get_value('TEST_OFFLINE_OBJECT_ID')
        else:
            print('测试环境为：生产环境')
            cls.store_id = cls.env_tool.get_value('PRO_OFFLINE_STORE_ID')
            cls.object_id = cls.env_tool.get_value('PRO_OFFLINE_OBJECT_ID')
        print(f'自动化测试用例中的DEBUG_MODEL为：{cls.bug_model},执行环境为：{cls.env}')

    def test_001_payment_success(self):
        """测试线下门店支付成功"""
        check_pay_status_data = {'orderNo': ""}
        # 1 创建订单（_createOrder）
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        create_order_id = order['result']['data']['objectId']
        # 2 获取支付参数（_createPolyPayment）
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(create_order_id)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        order_no = poly_payment['result']['data']['charge']['orderNo']
        # 2.1 接口参数赋值
        check_pay_status_data['orderNo'] = order_no
        # 3 mock payhook（修改支付结果保存的信息）
        print('# 3 mock payhook（修改支付结果保存的信息）')
        mock_payhook.MockPayHook().mock_payhook_v2(order_no=order_no, amount=1)
        # 4 获取支付结果（fetchPayResultByOrderNo）
        print('# 4 获取支付结果（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')

    def test_002_manual_cancel_order(self):
        """手动取消订单"""
        # 1 创建订单（_createOrder）
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        order_id = order['result']['data']['objectId']
        # 2 获取支付参数（_createPolyPayment）
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        # 3 手动取消订单（cancelOrder）
        print('# 3 手动取消订单（cancelOrder）')
        cancel_order = cancel_sale_activity_order.CancelSaleActivityOrder().cancel_sale_activity_order_v2(
            order_id=order_id)
        self.assertEqual(cancel_order, 'success', '手动取消订单接口返回状态异常', )
        # 4 查看订单状态
        print('# 4 查看订单状态')
        order_detail = common_order_detail.CommonOrderDetail().common_order(
            json={'orderId': order['result']['data']['objectId']})
        order_status = order_detail['result']['data']['order']['status']
        self.assertEqual(order_status, 'canceled', '订单状态不为已取消')

    def test_003_auto_cancel_order(self):
        """订单取消且退款"""
        # 1 创建订单
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        order_id = order['result']['data']['objectId']
        # 2 获取支付参数（_createPolyPayment）
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=order_id)
        order_no = poly_payment['result']['data']['charge']['orderNo']
        self.assertIsNotNone(order_no, '订单号为空')
        # 2.1 接口参数赋值
        # 3 mock payhook（修改支付结果保存的信息）
        print('# 3 mock payhook（修改支付结果保存的信息）')
        mock_payhook.MockPayHook().mock_payhook_v2(order_no=order_no, amount=1)
        # 4 获取支付结果（fetchPayResultByOrderNo）
        print('# 4 获取支付结果（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        # 5 执行退款
        print('# 5 执行退款')
        record = item_action_record.Item_Action_Record().item_action_record(order_id)
        self.assertEqual(record['result']['data']['status'], 'canceled', '断言订单状态失败')
        # 6 查询订单状态
        print('# 6 查询订单状态')
        detail = common_order_detail.CommonOrderDetail().order_detail(order_id)
        self.assertEqual('canceled', detail['result']['data']['order']['status'], '退款失败')

    @unittest.skipIf(check_test_is_build, '跳过测试')
    def test_004_auto_cancel_order(self):
        """自动取消订单"""
        # 1 创建订单（_createOrder）
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        create_order_id = order['result']['data']['objectId']
        # 2 获取支付参数（_createPolyPayment）
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=create_order_id)
        self.assertIsNotNone(poly_payment['result']['data']['charge']['orderNo'], '订单号为空')
        # 3 等待接口取消订单
        print('# 3 等待接口5min后自动取消订单')
        sleep(301)
        # 4 查看订单状态是否为已关闭
        print('# 4 查看订单状态是否为已关闭')
        order_detail = common_order_detail.CommonOrderDetail().common_order_v2(create_order_id)
        self.assertEqual('closed', order_detail, '订单状态不为已取消')

    def test_005_enter_wrong_channel(self):
        """输入错误的渠道 系统是否进行处理"""
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        order_id = order['result']['data']['objectId']
        payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=order_id, channel='xxx')
        self.assertEqual(payment['result']['error']['message'], '不支持该支付渠道', '渠道断言错误')

    def test_006_common_order_duplicate_sessionId(self):
        """common_order重复的sessionId 系统是否进行处理"""
        if self.env == 'TEST':
            session_id = '31e048f4-97eb-46a8-ace3-327906ac4eec'
        else:
            session_id = '989d91d0-f41a-4eed-ba89-a9f26571a060'
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id,
                                                               session_id=session_id)
        self.assertEqual('sessionId无效', order['result']['error']['message'], '重复的sessionId,系统未进行处理')

    def test_007_concurrent_payment(self):
        """并发生成订单 系统是否进行处理"""
        session_id = my_utils.get_uuid()

        def create_poly(order_id=None):
            result = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=order_id,
                                                                                         session_id=session_id)
            return result

        # 1 创建订单（_createOrder）
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id)
        create_order_id = order['result']['data']['objectId']
        print('# 2 获取支付参数（_createPolyPayment）')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 2 获取支付参数（_createPolyPayment）')
            future1 = executor.submit(create_poly, create_order_id)
            future2 = executor.submit(create_poly, create_order_id)
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

    def test_008_storeId_not_exist(self):
        """common_order时输入不存在的storeID"""
        order = submit_common_order.CommonOrder().common_order(store_id='', object_id=self.object_id, )
        self.assertEqual('门店不存在', order['result']['error']['message'], '不存在的storeID,系统未进行处理')

    def test_009_objectId_not_exist(self):
        """common_order时输入不存在的objectId"""
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id='')
        self.assertEqual('锁定库存失败', order['result']['error']['message'], '不存在的objectId,系统未进行处理')

    def test_010_concurrent_commonOrder(self):
        """并发创建订单，系统是否进行处理"""
        session_id = my_utils.get_uuid()
        print('# 1 并发创建订单（_createOrder）')

        def create_order(store_id=None, object_id=None):
            order = submit_common_order.CommonOrder().common_order(store_id=store_id, object_id=object_id,
                                                                   session_id=session_id)
            print(time.time())
            return order

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(create_order, self.store_id, self.object_id)
            future2 = executor.submit(create_order, self.store_id, self.object_id)
            # 获取线程函数的返回内容
            result1 = future1.result()
            result2 = future2.result()
            print(f"result1 = {result1}")
            print(f"result2 = {result2}")

            # 检查message是否为'sessionId无效'
            session_errors = [err.get('message') for err in
                              [result1.get('result', {}).get('error'), result2.get('result', {}).get('error')] if err]
            has_session_error = any(error == 'sessionId无效' for error in session_errors)

            # 检查result1和result2['result']['data']['objectId']是否存在
            object_ids = [res['result']['data'].get('objectId') for res in [result1, result2] if
                          res['result'].get('data')]
            has_object_id = all(obj_id is not None for obj_id in object_ids)
            self.assertTrue(has_session_error, "订单都失败")
            self.assertTrue(has_object_id, "订单重复生成")

    def test_011_createPolyPayment_duplicate_sessionId(self):
        """createPolyPayment传入重复的sessionID"""
        if self.env == 'TEST':
            session_id = 'e0d03aed-de0a-404d-ba29-a53b5917ca18',
        else:
            session_id = 'd8c6b756-7476-4516-868d-447fa20d8baf'
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id, )
        create_order_id = order['result']['data']['objectId']
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=create_order_id,
                                                                                           session_id=session_id)
        self.assertEqual(400, poly_payment['result']['error']['status'],
                         'createPolyPayment接口sessionId重复,系统未进行处理')
        self.assertEqual('正在获取支付状态，请稍后重试', poly_payment['result']['error']['message'],
                         'createPolyPayment接口sessionId重复,系统未进行处理')

    @unittest.skip('无效等价类')
    def test_012_createPolyPayment_wrong_orderid(self):
        """createPolyPayment传入错误的orderId,系统是否进行处理,并返回错误"""
        print('# 1 创建订单（_createOrder）')
        order = submit_common_order.CommonOrder().common_order(store_id=self.store_id, object_id=self.object_id, )
        create_order_id = order['result']['data']['objectId']
        wrong_order_id = create_order_id[:-1]
        print('# 2 获取支付参数（_createPolyPayment）')
        poly_payment = create_poly_payment.CreatePolyPayment().create_poly_payment_offline(order_id=wrong_order_id)
        self.assertEqual(400, poly_payment['result']['error']['status'],
                         'createPolyPayment传入orderid错误,系统未进行处理')

    def test_013_concurrent_refund_order(self):
        """订单并发取消且退款"""
        # 1 创建订单
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_no = order_data['order_no']
        order_id = order_data['order_id']
        # 2 mock payhook（修改支付结果保存的信息）
        print('# 2 mock payhook（修改支付结果保存的信息）')
        mock_payhook.MockPayHook().mock_payhook_v2(order_no=order_no, amount=1)
        # 3 获取支付结果（fetchPayResultByOrderNo）
        print('# 3 获取支付结果（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')

        # 4 并发执行退款
        def refund_order(order_id):
            record = item_action_record.Item_Action_Record().item_action_record(order_id)
            return record

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 4 并发执行退款')
            future1 = executor.submit(refund_order, order_id)
            future2 = executor.submit(refund_order, order_id)
            # 获取线程函数的返回内容
            result1 = future1.result()
            result2 = future2.result()
            print(f"result1 = {result1}")
            print(f"result2 = {result2}")
            status1 = result1.get('result', {}).get('data', {}).get('status')
            status2 = result2.get('result', {}).get('data', {}).get('status')
            # 确保至少一个status存在且为'canceled'
            if (status1 == 'canceled') or (status2 == 'canceled'):
                # 至少一个退款成功，可以根据需要决定是否需要具体打印哪一项成功
                pass  # 或者你可以在这里添加日志记录退款成功的详细信息
            else:
                # 如果两个都不存在或者都是空值，则断言失败
                if status1 is None and status2 is None:
                    self.fail('两个结果中status信息均缺失')
                elif status1 != 'canceled' and status2 is not None:
                    self.fail(f'退款未成功，result1状态为：{status1}')
                elif status2 != 'canceled' and status1 is not None:
                    self.fail(f'退款未成功，result2状态为：{status2}')
                else:  # 这个分支理论上不会执行，除非上面的逻辑有误
                    self.fail('未知错误，两个退款状态均不符合预期')

        # 5 查询订单状态
        print('# 5 查询订单状态')
        order_detail = detail_ui_config_data.DetailUIConfigData().detail_ui_config_data_v2(order_id)
        # refund_id = order_detail['result']['data']['sections'][4]['value']['refundList'][0]['refundId']
        # self.assertIsNotNone(refund_id, '退款信息查询失败')

    def test_014_cancel_order_orderId_is_null(self):
        """退款订单，orderId为空"""
        # 1 创建订单
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_no = order_data['order_no']
        print(order_data)
        # 2 mock payhook（修改支付结果保存的信息）
        print('# 2 mock payhook（修改支付结果保存的信息）')
        mock_payhook.MockPayHook().mock_payhook_v2(order_no=order_no, amount=1)
        # 3 获取支付结果（fetchPayResultByOrderNo）
        print('# 3 获取支付结果（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        print('# 4 执行退款')
        record = item_action_record.Item_Action_Record().item_action_record(order_id='')
        self.assertEqual(record['result']['error']['status'], 400, '退款传入空订单id也能执行退款')

    def test_015_manual_cancel_order_wrong_order_id(self):
        """手动取消订单传入错误的order_id时"""
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_id = order_data['order_id']
        worrng_order_id = order_id[:-1]
        print('# 2 手动取消订单（cancelOrder）')
        cancel_order = cancel_sale_activity_order.CancelSaleActivityOrder().cancel_sale_activity_order(
            order_id=worrng_order_id)
        self.assertEqual(cancel_order['result']['data']['status'], 'failure', '手动取消订单接口返回状态异常', )
        self.assertEqual(cancel_order['result']['data']['errorCode'], -5, '手动取消订单接口返回状态异常', )
        self.assertEqual(cancel_order['result']['data']['errorMsg'], '未查询到订单数据',
                         '手动取消订单接口返回状态异常', )
        print('# 3 查看订单状态')
        order_detail = common_order_detail.CommonOrderDetail().common_order_v2(order_id=order_id)
        self.assertEqual(order_detail, 'created', '订单状态与预期不符')

    def test_016_refunds_in_case_of_unpaid_orders(self):
        """订单创建后直接执行退款接口"""
        action_record_json_data = {
            'funcName': 'cancelOrder',
            'params': {
                'orderId': '',
            },
        }

        # 1 创建订单
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_no = order_data['order_no']
        order_id = order_data['order_id']
        action_record_json_data['params']['orderId'] = order_id
        print('# 2 执行退款 ')
        record = item_action_record.Item_Action_Record().item_action_record(order_id)
        order_status = record['result']['data']['status']
        self.assertEqual(order_status, 'canceled', '订单状态不为已取消')

    def test_017_concurrent_execution_of_order_cancel_order_after_order_creation(self):
        """订单创建后并发执行取消订单接口"""
        # 1 创建订单
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_id = order_data['order_id']

        def cancel_order(order_id=order_id):
            print(time.time())
            cancel_order = cancel_sale_activity_order.CancelSaleActivityOrder().cancel_sale_activity_order_v2(order_id)
            return cancel_order

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            print('# 2 并发执行取消订单')
            result1_status = executor.submit(cancel_order, order_id)
            result2_status = executor.submit(cancel_order, order_id)
            # 获取线程函数的返回内容
            print(f"result1_status = {result1_status}")
            print(f"result2_status = {result2_status}")
            try:
                if result1_status == 'success' and result2_status == 'success':
                    raise Exception('订单并发去执行取消退款逻辑错误')
                else:
                    print('result1_status == result2_status ')
            except Exception as e:
                self.assertEqual("'objectId'", str(e), '订单重复生成系统未进行处理')

        print('# 4 查看订单状态')
        order_detail = common_order_detail.CommonOrderDetail().common_order(json={'orderId': order_id})
        order_status = order_detail['result']['data']['order']['status']
        self.assertEqual(order_status, 'canceled', '订单状态不为已取消')

    def test_018_paysuccess_pick_up_number_assert(self):
        """支付成功后，查询订单状态，订单状态为已支付，且有自提码"""
        # 1 创建订单
        print('# 1 创建订单（_createOrder）并且获取支付参数（_createPolyPayment）')
        order_data = create_order_and_payment.CreateOrderAndPayment.create_offline_order_and_payment(
            store_id=self.store_id, object_id=self.object_id)
        order_no = order_data['order_no']
        order_id = order_data['order_id']
        print(order_data)
        # 2 mock payhook（修改支付结果保存的信息）
        print('# 2 mock payhook（修改支付结果保存的信息）')
        mock_payhook.MockPayHook().mock_payhook_v2(order_no=order_no, amount=1)
        # 3 获取支付结果（fetchPayResultByOrderNo）
        print('# 3 获取支付结果（fetchPayResultByOrderNo）')
        status = my_utils.poll_order_status(
            callable_obj=pay_result_by_order_no.PayResultByOrderNo().get_order_status_by_order_no,
            success_code='success', order_no=order_no)
        self.assertTrue(status, '订单未完成支付，支付结果断言不正确')
        print('# 4 查看订单状态(fetchCommonOrderDetail)')
        time.sleep(0.5)
        order_detail = CommonOrderDetail().order_detail(order_id=order_id)
        order_pick_up_code = order_detail['result']['data']['order']['attrs']['orderSn']
        self.assertIsNotNone(order_pick_up_code, '断言自提码为空')


if __name__ == '__main__':
    unittest.main()
