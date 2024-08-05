# -*- coding: utf-8 -*-
# @Time    : 2023/12/26 18:35
# @Author  : Leexzyy
# @Site    : 
# @File    : user_energy_info.py
# @Software: PyCharm
from utils import mongod_utils
from userInfo import user_info


def link_eng_trans_to_database():
    """
    链接数据库获取用户信息
    :return:
    """
    user_id = user_info.get_user_id()
    user = mongod_utils.find_documents('saturnbird', 'EnergyTrans',
                                       {'_p_user': f'_User${user_id}'})
    return user


def get_user_eng_list():
    """
    获取用户积分列表
    :return:
    """
    user_add_point_list = link_eng_trans_to_database()
    deduction_list = []
    for i in user_add_point_list:
        deduction_list.append(i['energyCnt'])
    return deduction_list


if __name__ == '__main__':
    # {'point_available': 1186098, 'point_total': 1209898, 'point_used': 23800}
    user = get_user_eng_list()
    print(user)
    print(sum(user))
    # user = link_pnt_trans_to_database()
    # for i in user:
    #     print(i)
