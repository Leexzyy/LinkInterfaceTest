# -*- coding: utf-8 -*-
# @Time    : 2024/1/25 10:45
# @Author  : Leexzyy
# @Site    : 
# @File    : test_energy_order_payment.py.py
# @Software: PyCharm
import time
import unittest
# from threading import Thread

from services.mini.check_order_status import fetch_data_by_traceId, common_order_detail
from services.mini.submit_order import submit_energy_order_async
from services.admin import item_action_record
from utils import env_utils, my_utils
from userInfo import user_info
import get_path_info


class TestEnergyOrderPayment(unittest.TestCase):
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
            cls.store_id = cls.env_tool.get_value('TEST_ENERGY_STORE_ID')
            cls.object_id = cls.env_tool.get_value('TEST_ENERGY_OBJECT_ID')
        else:
            print('测试环境为：生产环境')
            cls.store_id = cls.env_tool.get_value('PRO_ENERGY_STORE_ID')
            cls.object_id = cls.env_tool.get_value('PRO_ENERGY_OBJECT_ID')
        print(f'自动化测试用例中的DEBUG_MODEL为：{cls.bug_model},执行环境为：{cls.env}')

    def tearDown(self):
        print('---------------用例执行完毕清除能量----------------')
        user_energy_after = user_info.get_user_energy_available()
        print(f'用户执行 testcase 后可用能量:{user_energy_after}')
        item_action_record.Item_Action_Record().user_remove_energy(user_energy_after)
        user_init_energy = user_info.get_user_energy_available()
        print(f'用户执行初始化后可用能量:{user_init_energy}')

    @unittest.skip('增加能量接口精度丢失 等待修复完成将打开此条用例')
    def test_001_energy_payment_success(self):
        """能量商品下单成功"""
        print('# 1:获取用户 下单前的能量')
        user_init_energy = user_info.get_user_energy_available()
        print(f'用户可用能量：{user_init_energy}')
        if int(user_init_energy) < 1:
            print('能量不足，增加能量')
            item_action_record.Item_Action_Record().user_add_energy(1)
            time.sleep(1)
            user_add_energy = user_info.get_user_energy_available()
            print(f'用户增加能量后可用能量：{user_add_energy}')
        print('# 2 : 调用下单接口生成订单 (submit_energy_order_async)')
        energy = submit_energy_order_async.SubmitEnergyOrderAsyncAPI().submit_energy_order_async(
            store_id=self.store_id, object_id=self.object_id, qty=1)
        self.assertIsNotNone(energy['result']['data']['traceId'], '生成traceId失败')
        traceid = energy['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertIsNotNone(order_detail['result']['data']['data'][0]['objectId'], '生成orderid失败')
        order_id = order_detail['result']['data']['data'][0]['objectId']
        print("#4 判断订单状态")
        order_state = common_order_detail.CommonOrderDetail().common_order_v2(order_id)
        self.assertEqual(order_state, 'paid', '订单状态与预期不符')
        print("#5 用户积分扣除数量时候等于商品价格")
        time.sleep(1)
        user_energy_after = user_info.get_user_energy_available()
        print(f'用户购买商品后可用能量:{user_energy_after}')
        self.assertEqual(user_energy_after - user_init_energy, 0, '用户能量扣除不正确')

    def test_002_energy_insufficient_payment_error(self):
        """能量商品能量不足下单失败"""
        print('# 1:获取用户 下单前的能量')
        user_init_energy = user_info.get_user_energy_available()
        print(f'用户可用能量{user_init_energy}')
        if int(user_init_energy) > 0:
            print('用户有能量，能量清空')
            item_action_record.Item_Action_Record().user_remove_energy(user_init_energy)
        print('# 2 : 调用下单接口生成订单 (submit_energy_order_async)')
        energy = submit_energy_order_async.SubmitEnergyOrderAsyncAPI().submit_energy_order_async(
            store_id=self.store_id, object_id=self.object_id, qty=1)
        self.assertIsNotNone(energy['result']['data']['traceId'], '生成traceId失败')
        traceid = energy['result']['data']['traceId']
        print("#3 获取orderid")
        order_detail = fetch_data_by_traceId.DataByTraceIdAPI().data_by_trace_id(traceid)
        self.assertEqual(1, order_detail['result']['data']['code'], 'code状态有误')
        self.assertEqual('能量不足', order_detail['result']['data']['data']['error']['message'],
                         '能量不足message断言失败')
        self.assertEqual(400, order_detail['result']['data']['data']['error']['status'], '能量不足status断言失败')


if __name__ == '__main__':
    unittest.main()
