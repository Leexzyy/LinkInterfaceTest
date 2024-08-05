# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 10:23
# @Author  : Leexzyy
# @Site    : 
# @File    : oss_utils.py
# @Software: PyCharm
import oss2
import get_path_info
from common import config
from utils import env_utils
import get_path_info
path = get_path_info.get_path()
env_tool = env_utils.EnvTool(f'{path}/payment.env')


def file_upload(file_path, oss_file_path):
    """
    上传文件到阿里云oss
    :param file_path: 本地文件路径
    :param oss_file_path: 阿里云oss文件名称
    """
    auth = oss2.Auth(env_tool.get_value('OSS_ACCESS_KEY_ID'), env_tool.get_value('OSS_ACCESS_KEY_SERCET'))
    bucket = oss2.Bucket(auth,env_tool.get_value('OSS_END_POINT'), env_tool.get_value('OSS_BUCKET_NAME'))
    bucket.put_object_from_file(key=oss_file_path, filename=file_path)


if __name__ == '__main__':
    object_name = '11-31-20Payment_Report.html'
    local_file_name = f'{get_path_info.get_path()}/report/2023-12-18/{object_name}'
    file_upload(local_file_name, object_name)
