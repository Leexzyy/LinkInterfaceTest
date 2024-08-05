# -*- coding:utf-8 -*-
"""
@Author: Leexzyy
@File:  my_utils.py
@CreateTime:  2021-08-03
@desc:
@APIURL:
"""

import random
import time
import uuid

import jsonpath

import get_path_info
from utils import env_utils


# 生成UUID
def get_uuid():
    s_uuid = str(uuid.uuid4())
    return s_uuid


# 裁剪string类型的内容
def key_string_cut(key):
    return key[2:-2]


# 封装jsonpath
def get_json(json, key):
    return jsonpath.jsonpath(json, key)


def json_string(json, key):
    return get_json(json, key)[0]


def json_int(json, key):
    return get_json(json, key)[0]


def random_order_num():
    """
    随机生成15位数字的订单号
    """
    return ''.join((str(random.choice(range(10))) for _ in range(15)))


def get_env():
    """
    获取ENV环境
    """
    path = get_path_info.get_path()
    env_tool = env_utils.EnvTool(f'{path}/payment.env')
    env = env_tool.get_value('ENV')
    return env


def get_env_tools():
    """
    获取ENVtools
    """
    path = get_path_info.get_path()
    env_tool = env_utils.EnvTool(f'{path}/payment.env')
    return env_tool


def poll_order_status(callable_obj, attempts=10, interval=1, success_code=None, *args, **kwargs):
    for _ in range(attempts):
        print(f'轮训器循环检查第 {_+1} 次')
        result = callable_obj(*args, **kwargs)  # 将参数传递给方法
        print(f"轮训器查询的参数为: {result}")
        if result == success_code:
            print("轮训器检查断言正确，结束循环")
            return True
        print("轮训器检查断言错误，结束循环")
        time.sleep(interval)
    return False


if __name__ == '__main__':
    print(random_order_num())
