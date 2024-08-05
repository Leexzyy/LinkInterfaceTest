# -*- coding:utf-8 -*-
"""
@Author: Leexzyy
@File:  run_test_interface_api.py
@CreateTime:  2021-06-10
@desc: 接口自动化系统入口
@APIURL:
"""
import logging
import os
import unittest
from datetime import datetime
import get_path_info
from common import config
from my_beautiful_report import BeautifulReport as bf
from utils import oss_utils, fly_msg_util, env_utils, my_utils

env = my_utils.get_env()
now = datetime.now()
folder_time_name = now.strftime('%Y-%m-%d')
report_time_name = now.strftime('%H-%M-%S')
folder_name = 'report/' + folder_time_name
report_root_path = ''
correct_rate = ''
case_fail = ''
report_dir = {'all_case': 0, 'case_success': 0, 'case_fail': 0, 'case_error': 0, 'case_skip': 0, 'correct_rate': 0,
              'case_time': 0}

report_name = report_time_name + config.REPORT_NAME
path = get_path_info.get_path()
report_path = os.path.join(path, 'report', folder_time_name, report_name + '.html')
report_url = ''
env_tool = env_utils.EnvTool(f'{path}/payment.env')
test_report_url = f"http://autotest.bfelab.com/payment_report/{folder_time_name}/{report_name}.html"
oss_report_url = None


def create_report_folder():
    global report_root_path
    report_root_path = get_path_info.get_path() + '/' + folder_name
    os.makedirs(report_root_path, 0o777, exist_ok=True)


def run_interface_test_and_create_report():
    global correct_rate, case_fail
    # 存放测试用例文件夹
    test_dir = path + "/testCase"
    dis = unittest.defaultTestLoader.discover(test_dir, pattern='test_*.py')
    runner = bf(dis)
    runner.report(
        description=config.REPORT_TITLE,
        report_dir='' + report_root_path,
        filename=report_name  # 生成测试报告的文件名
    )
    case_success = runner.success_count
    # print('运行成功数量 == ' + str(case_success))
    fields = runner.fields
    # print('fields === ' + str(fields))
    all_case = fields['testAll']
    case_fail = fields['testFail']
    case_error = fields['testError']
    case_time = fields['totalTime']
    case_skip = fields['testSkip']
    if case_fail == 0:
        correct_rate = 100
    else:
        fail_correct = case_fail / all_case
        correct_rate = 1 - fail_correct
        correct_rate = correct_rate * 100
        correct_rate = round(correct_rate, 2)

    print(
        f"一共运行{all_case}测试用例,成功{case_success}条,失败{case_fail}条,超时{case_error}条,跳过{case_skip}条,成功率 {correct_rate}%,执行时间{case_time},")
    report_dir['all_case'] = all_case
    report_dir['case_success'] = case_success
    report_dir['case_fail'] = case_fail
    report_dir['case_error'] = case_error
    report_dir['case_skip'] = case_skip
    report_dir['correct_rate'] = correct_rate
    report_dir['case_time'] = case_time


def upload_report():
    global report_url
    # 生成OSS路径
    oss_path = config.OSS_PATH + '/' + folder_time_name + '/' + report_name + '.html'
    # 上传文件到OSS
    oss_utils.file_upload(report_path, oss_path)
    # 返回文件的URL地址
    report_url = f"https://xxx.oss-cn-shenzhen.aliyuncs.com/{oss_path}"
    return report_url


def send_feishu_msg():
    content = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**{env}环境测试报告结果：**\n一共运行<font color='green'> {report_dir['all_case']} </font>条测试用例,成功<font color='green'> {report_dir['case_success']} </font>条,失败<font color='red'> {report_dir['case_fail']} </font>条,超时<font color='yellow'> {report_dir['case_error']} </font>条,跳过 {report_dir['case_skip']} 条,成功率 <font color='green'> {report_dir['correct_rate']} %</font>,执行时间<font color='green'> {report_dir['case_time']}</font>。\n"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "点击查看报告"
                            },
                            "type": "primary",
                            "multi_url": {
                                "url": f"{test_report_url}",
                                "pc_url": "",
                                "android_url": "",
                                "ios_url": ""
                            }
                        }
                    ]
                }
            ],
            "header": {
                "template": "blue",
                "title": {
                    "content": f"{env}环境三顿半daily-build测试报告",
                    "tag": "plain_text"
                }
            }
        }

    }
    fly_msg_util.send_fly_msg(content)


def run_test():
    debug_model = env_tool.get_value('DEBUG_Model')
    print(f'DEBUG_Model 值为：{debug_model}')
    if debug_model == 'False':
        print('非DEBUG模式')
        create_report_folder()
        run_interface_test_and_create_report()
        oss_report_url = upload_report()
        send_feishu_msg()
        print(f'运行成功,测试报告已经上传至：{oss_report_url}')
        return f"测试报告结果：\n一共运行 {report_dir['all_case']} 条测试用例,成功{report_dir['case_success']},失败{report_dir['case_fail']} 条,超时{report_dir['case_error']}条,跳过 {report_dir['case_skip']} 条,成功率  {report_dir['correct_rate']} %,执行时间{report_dir['case_time']}。\n"
    else:
        print('DEBUG模式')
        create_report_folder()
        run_interface_test_and_create_report()
        return f"测试报告结果：\n一共运行 {report_dir['all_case']} 条测试用例,成功{report_dir['case_success']},失败{report_dir['case_fail']} 条,超时{report_dir['case_error']}条,跳过 {report_dir['case_skip']} 条,成功率  {report_dir['correct_rate']} %,执行时间{report_dir['case_time']}。\n"


if __name__ == '__main__':
    run_test()
