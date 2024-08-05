# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 14:28
# @Author  : Leexzyy
# @Site    : 
# @File    : user_info.py
# @Software: PyCharm


from utils import mongod_utils, my_utils
from userInfo import user_point_info, user_energy_info


def link_user_to_database():
    """
    链接数据库获取用户信息
    :return:
    """
    env_tool = my_utils.get_env_tools()
    if my_utils.get_env() != 'TEST':
        phone = env_tool.get_value('PRO_PHONE')
        print('数据库链接环境：PRO')
    else:
        phone = env_tool.get_value('TEST_PHONE')
        print('数据库链接环境：TEST')
    user = mongod_utils.find_documents('saturnbird', '_User', {'mobilePhoneNumber': phone})
    return user


def get_user_id():
    """
    获取用户id
    :return:
    """
    user = link_user_to_database()
    for i in user:
        return i['_id']


def get_user_balance():
    """
    获取用户余额
    :return:
    """
    user = link_user_to_database()
    for i in user:
        return i['balance']


def get_user_point():
    """
    获取用户积分/顿点
    :return:
    """
    user_balance = get_user_balance()
    user_point = {'point_available': user_balance['point']['available'], 'point_total': user_balance['point']['total'],
                  'point_used': user_balance['point']['used']}
    return user_point


def get_user_point_available():
    """
    获取用户积分可用
    :return:
    """
    user_balance = get_user_balance()
    user_point = {'point_available': user_balance['point']['available'], 'point_total': user_balance['point']['total'],
                  'point_used': user_balance['point']['used']}
    return user_point['point_available']


def get_user_energy():
    """
    获取用户能量
    :return:
    """
    user_balance = get_user_balance()
    user_energy = {'energy_available': user_balance['energy']['available'],
                   'energy_total': user_balance['energy']['total'],
                   'energy_used': user_balance['energy']['used']}
    return user_energy


def get_user_energy_available():
    """
    获取用户能量可用
    :return:
    """
    user_balance = get_user_balance()
    return user_balance['energy']['available']/100


def check_user_point():
    """
    检查用户积分/顿点 与PntTrans表的记录结果是否一致
    :return:
    """
    check_point_used = None
    user_point = get_user_point()  # 用户表 用户积分情况
    point_used = user_point['point_used']  # 用户表 用户积分使用总和
    user_point_list = user_point_info.get_user_point_list()  # 用户表 用户积分使用列表
    trans_negative_sum = sum([num for num in user_point_list if num < 0])  # 消费记录表里所有扣款积分总和
    trans_user_point_for_admin_deduct = sum(user_point_info.get_admin_deduct_print_list())  # 消费记录表里管理员扣除积分总和
    trans_user_point_for_expired = sum(user_point_info.get_point_expired_list())  # 消费记录表里用户积分过期记录
    negative_sum = trans_negative_sum - trans_user_point_for_admin_deduct - trans_user_point_for_expired  # 消费记录表中用户最终使用积分
    if abs(negative_sum) == point_used:
        check_point_used = True
    else:
        check_point_used = False
    if sum(user_point_list) == user_point['point_available'] and user_point['point_available'] == user_point[
        'point_total'] - user_point['point_used'] and check_point_used:
        return True
    else:
        return False


# todo:验证用户顿点/积分是否正确，验证用户能量是否正确


if __name__ == '__main__':
    # print(get_user_point())
    print(get_user_energy_available())
    # print(check_user_point())
    # print(get_user_id())
    # print(f"用户积分详情：{get_user_point()}")
    # print(f"用户能量详情：{get_user_energy()}")
    # print(f"用户使用积分记录：{user_point_info.get_user_point_list()}")
    # print(f"系统扣除积分记录：{user_point_info.get_admin_deduct_print_list()}")
    # print(f"用户使用积分余额：{sum(user_point_info.get_user_point_list())}")
    # print(f'用户使用积分记录：{[num for num in user_point_info.get_user_point_list() if num < 0]}')
    # print(f'用户使用积分总和：{sum([num for num in user_point_info.get_user_point_list() if num < 0])}')
    # print(f'用户获得积分记录：{[num for num in user_point_info.get_user_point_list() if num > 0]}')
    # print(f'用户获得积分总和：{sum([num for num in user_point_info.get_user_point_list() if num > 0])}')
    # print(f"用户使用能量记录：{user_energy_info.get_user_eng_list()}")
    # print(f"用户使用能量余额：{sum(user_energy_info.get_user_eng_list())}")

    # point = check_user_point()
    # print(point)
    # user = get_user_energy()
    # print(user)
    # user = link_deduction_pnt_trans_to_database()
    # for i in user:
    #     print(i)
    # print(user)
