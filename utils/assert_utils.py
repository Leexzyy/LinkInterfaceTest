# -*- coding:utf-8 -*-
"""
@Author: Leexzyy
@File:  assert_utils.py
@CreateTime:  2022-03-21
@desc: 封装智能断言方法 ，后续有啥智能断言方法可以封装在此
@APIURL:
"""

import loguru

from common import config


def assert_requests(self, request=None, assert_time=1):
    """
    封装断言基本的requests内容
    :param: self  传入unittest对象 用来获取断言内容
    :param: request  传入requests对象 用来获取响应时间以及响应状态码
    :param: assert_time  断言时间 用来断言该接口的响应速度 默认为1
    """
    requests_time = request.elapsed.total_seconds()
    requests_status_code = request.status_code
    self.assertLessEqual(requests_time, assert_time, f'接口响应时间达不到预期时间，该接口响应时间为 {requests_time} !')
    self.assertEqual(requests_status_code, config.STATUS_CODE, f'接口响应码不为200，该接口响应码为 {requests_status_code}!')


def assert_data(self, request=None, assert_time=15, **kwargs):
    """
     封装智能断言busicode以及msg以及data
    :param: self  传入unittest对象 用来获取断言内容
    :param: request  传入requests对象 接口传入的msg以及busicode
    :param: kwargs  传入yaml文件 智能解析yaml文件是否符合要求
    ⚠️ YAML文件必须按照规范写入
    默认智能断言busicode以及msg
    此智能断言data内容支持三种断言模式 ：
    1⃣️ 传入参数为：data 为断言data所有内容是否于接口出参相同 （全量对比）
    2⃣️ 传入参数为：data_in 为断言预期值是否与出参所有的key值断言 （部分对比）
    3⃣️ 传入参数为 data_len 为断言出参长度是否符合预期（对比长度）
    """
    assert_requests(self, request, assert_time)
    my_assert = kwargs['assert']
    my_busicode = my_assert.get('busicode')
    my_msg = my_assert.get('msg')
    my_data = my_assert.get('data')
    my_data_len = my_assert.get('data_len')
    my_data_in = my_assert.get('data_in')
    print('接口请求头部' + str(kwargs.get('headers')))
    if my_busicode is None:
        loguru.logger.error('此YAML文件传入busicode有误且为必填项 请检查YAML文件是否符合规范')
    if my_msg is None:
        loguru.logger.error('此YAML文件传入msg有误且为必填项 请检查YAML文件是否符合规范')

    # 断言接口的busiCode是否和预期一致
    self.assertEqual(my_busicode, request.json()['busiCode'],
                     f"智能断言！【接口的busiCode于预期不一致】，该接口busiCode为 {request.json()['busiCode']} !")
    self.assertEqual(my_msg, request.json()['msg'], f"智能断言！【接口的msg于预期不一致】，该接口msg为 ：{request.json()['msg']} !")

    if my_data_len is not None:
        self.assertEqual(my_data_len, len(request.json()['data']),
                         f"智能断言！【接口的data_len于预期不一致】，该接口data_len为 ：{len(request.json()['data'])} !")

    if my_data is not None:
        self.assertEqual(my_data, request.json()['data'], f"智能断言！【接口的data于预期不一致】，该接口data为 ：{request.json()['data']} !")

    if my_data_in is not None:
        try:
            loguru.logger.info('循环字典')

            def print_key_value_all(input_json):
                """
                循环遍历json方法 且智能断言yaml文件中的value
                """
                if isinstance(input_json, dict):
                    for key in input_json.keys():
                        key_value = input_json.get(key)
                        if isinstance(key_value, dict):
                            print_key_value_all(key_value)
                        elif isinstance(key_value, list):
                            for json_array in key_value:
                                print_key_value_all(json_array)
                        else:
                            loguru.logger.info(f'循环遍历json智能断言对比 key_value: {key} : {key_value}')
                            self.assertIn(str(key_value), str(request.json()['data']))
                elif isinstance(input_json, list):
                    for input_json_array in input_json:
                        print_key_value_all(input_json_array)

            print_key_value_all(my_data_in)
        except Exception as e:
            print(e)
            self.assertIn(my_data_in, request.json()['data'], f"智能断言！【接口data_in断言错误】接口为list")
