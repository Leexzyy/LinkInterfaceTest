# -*- coding: utf-8 -*-
# @Time    : 2023/12/22 10:22
# @Author  : Leexzyy
# @Site    : 
# @File    : bash_api.py
# @Software: PyCharm

import requests
from common import config
import loguru
from utils import my_utils


class BashApi:
    base_url = None
    headers = None
    env = my_utils.get_env()
    env_tool = my_utils.get_env_tools()
    if env != 'PRO':
        print('env = 测试环境!')
        base_url = env_tool.get_value('BASE_TEST_URL')
        headers = config.TEST_HEADERS
        print(headers)
    else:
        print('env = 生产环境!')
        base_url = env_tool.get_value('BASE_PRO_URL')
        headers = config.PRO_HEADERS
        print(headers)

    def bash_request(self, method='post', url=None, headers=headers, cookies=None, json=None,
                     timeout=config.INTERFACE_TIME_OUT, status_code=config.STATUS_CODE):
        """
        bashAPI
        :param method:默认是post请求
        :param url:
        :param headers: 默认配置请求头
        :param cookies:
        :param json: 传入json
        :param timeout: 默认200ms超时
        :param status_code: status_code断言 默认为200 特殊情况导致接口status_code不为200时可以传入 用来断言接口响应吗
        :return:
        """

        try:
            url_name = url.split('/')[-1]
            url = self.base_url + url
            print(f'调用接口：{url_name}')
            print(f'调用{url_name}接口请求头 ：{headers}')
            print(f'调用{url_name}接口入参 ： {json}')
            response = requests.session().request(method=method, url=url, headers=headers, cookies=cookies,
                                                  json=json,
                                                  timeout=timeout)
            print(f'调用{url_name}接口接口返回内容： {response.text}')
            print(f'调用{url_name}接口接口响应时间： {response.elapsed.total_seconds()}')
            assert response.status_code == status_code, f"接口响应码响应不为预期，请检查接口响应码符合预期,现接口响应码现在为{response.status_code}"
            return response.json()
        except requests.exceptions.Timeout:
            loguru.logger.error(f"---{url_name}---requests 请求超时")
            print(f"---{url_name}---requests 请求超时")
        except Exception as e:
            loguru.logger.error("requests 请求错误 : %s" % e)
            print("requests 请求错误 : %s" % e)

    def admin_api(self, method='post', url=None, json=None,
                  timeout=config.INTERFACE_TIME_OUT, status_code=config.STATUS_CODE):
        """
        admin_api 后台管理系统的bash api
        :param method: 默认是post请求
        :param url:    传入url
        :param json:   传入json
        :param timeout: 默认200ms超时
        :param status_code: status_code断言 默认为200 特殊情况导致接口status_code不为200时可以传入 用来断言接口响应吗
        """
        if self.env != 'PRO':
            headers = config.TEST_ADMIN_HEADERS
            # cookies = config.TEST_ADMIN_COOKIES
        else:
            headers = config.PRO_ADMIN_HEADERS
            # cookies = None
        api = BashApi().bash_request(method=method, url=url, headers=headers, json=json,
                                     timeout=timeout, status_code=status_code)
        return api


if __name__ == '__main__':
    api = BashApi()
    # 调用bash_api方法发送请求
    result = api.bash_api()
