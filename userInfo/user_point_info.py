# -*- coding: utf-8 -*-
# @Time    : 2023/12/26 18:13
# @Author  : Leexzyy
# @Site    : 
# @File    : user_point_info.py
# @Software: PyCharm
from utils import mongod_utils
from userInfo import user_info


def link_pnt_trans_to_database():
    """
    链接数据库获取用户信息
    :return:
    """
    user_id = user_info.get_user_id()
    user = mongod_utils.find_documents('saturnbird', 'PntTrans',
                                       {'_p_user': f'_User${user_id}'})
    return user


def get_user_point_list():
    """
    获取用户积分列表
    :return:
    """
    user_add_point_list = link_pnt_trans_to_database()
    deduction_list = []
    for i in user_add_point_list:
        deduction_list.append(i['amount'])
    return deduction_list


def get_point_expired_list():
    """
    获取用户积分过期列表
    :return:
    """

    user_id = user_info.get_user_id()
    # user_id = 'xyERjYlmi2lMJZfSBuTpvKM2'
    user = mongod_utils.find_documents('saturnbird', 'PntTrans',
                                       {'actionDetail': {"action": "expired", "desc": [{"text": "顿点已过有效期"}]},
                                        '_p_user': f"_User${user_id}"})
    expired_list = []
    # 将cursor转化成list 用来判断是否为空
    user_list = list(user)
    if len(user_list) != 0:
        for i in user_list:
            print(i['amount'])
            expired_list.append(i['amount'])
        return expired_list
    else:
        print('用户无过期积分')
        return expired_list


def get_admin_deduct_print_list():
    """
    获取用户管理员扣除积分列表
    :return:
    """
    user_id = user_info.get_user_id()
    query = {'_p_user': f'_User${user_id}', "actionDetail.action": 'ADMIN_DEDUCT_POINT'}
    user = mongod_utils.find_documents('saturnbird', 'PntTrans',
                                       query)
    user_list = list(user)
    admin_deduct_print_list = []

    if len(user_list) != 0:
        for i in user_list:
            # print(i)
            # print(i['amount'])
            admin_deduct_print_list.append(i['amount'])
        return admin_deduct_print_list
    else:
        print('无管理员扣除积分')
        return admin_deduct_print_list


if __name__ == '__main__':
    # user_prn_trans = link_pnt_trans_to_database()
    # for i in user_prn_trans:
    #     print(i)
    # expired_list = get_point_expired_list()
    # print(expired_list)
    print(get_admin_deduct_print_list())
