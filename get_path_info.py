# -*- coding:utf-8 -*-
"""
@Author: Leexzyy
@File:  get_path_info.py
@CreateTime:  2021-06-15
@desc:获取工程根目录 D:\TestProject\testcolletionapi\eHomeInterfaceTest\
"""
import os


def get_path():
    path = os.path.split(os.path.realpath(__file__))[0]
    return path


if __name__ == '__main__':  # 执行该文件，测试下是否OK
    print('测试路径是否OK,路径为：', get_path())
