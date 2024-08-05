# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 16:39
# @Author  : Leexzyy
# @Site    : 
# @File    : fly_msg_util.py
# @Software: PyCharm
from common import config
from utils import env_utils
import get_path_info


def send_fly_msg(content):
    """
    发送飞书机器人消息

    参数:
    token (str): 飞书机器人的token。
    to (str): 接收消息的用户或群组的id。
    content (str): 消息内容。

    返回:
    bool: 发送是否成功。
    """
    path = get_path_info.get_path()
    env_tool = env_utils.EnvTool(f'{path}/payment.env')
    import requests
    headers = {
        'Content-Type': 'application/json',
    }
    url = env_tool.get_value('FEISHU_HOOK')
    try:
        response = requests.post(url, headers=headers, json=content)
        response_json = response.json()
        return response_json['result']['msgId']
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    msg = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "自动化测试报告通知",
                    "content": [
                        [{
                            "tag": "text",
                            "text": "Payment_Report测试报告"
                        },
                            {
                                "tag": "text",
                                "text": "测试报告结果：一共运行1测试用例,成功1条,失败0条,跳过0条,成功率 100%,执行时间1s。"

                            },
                            {
                                "tag": "a",
                                "text": "测试报告请查看",
                                "href": "https://bfe-autotest.oss-cn-shenzhen.aliyuncs.com/auto-test-pay/2023-12-15/16-06-44Payment_Report.html"
                            },

                        ]
                    ]
                }
            }
        }
    }
    msg1 = {
        "type": "template",
        "data": {
            # // 卡片 ID，参数必填。
            "template_id": "ctp_AAyij2MUMnCM",
            "template_variable":
                {
                    "title": "Payment",
                    "test_case": 1,
                    "success_nub": 12,
                    "error_nub": 13,
                    "skip_nub": 14,
                    "success_rate": 99,
                    "report_url": "https://bfe-autotest.oss-cn-shenzhen.aliyuncs.com/auto-test-pay/2023-12-15/16-06-44Payment_Report.html",
                    "run_time": "32"
                }
        }
    }
    msg3 = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": "**测试报告结果：**\n一共运行<font color='green'> ${test_case} </font>条测试用例,成功<font color='green'> ${success_nub} </font>条,失败<font color='red'> ${error_nub} </font>条,跳过 ${skip_nub} 条,成功率 <font color='green'> ${success_rate} %</font>,执行时间<font color='green'> ${run_time}s</font>。\n"
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
                                "url": "https://bfe-autotest.oss-cn-shenzhen.aliyuncs.com/auto-test-pay/2023-12-15/16-06-44Payment_Report.html",
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
                    "content": "${title}测试报告",
                    "tag": "plain_text"
                }
            }
        }

    }
    send_fly_msg(msg3)
