# -*- coding:utf-8 -*-
"""
@Author: Leexzyy
@File:  send_email_report.py
@CreateTime:  2021-06-11
@desc: 发送邮件类
"""
import os
import time

import yagmail

from common import config

get_cwd = os.getcwd()
my_file = get_cwd + "\EHomeInterfaceTest.html"
title_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class SendEmail():

    def yagmail(self, file, report_dir):
        print('正在发送测试报告')
        try:
            yag = yagmail.SMTP(user=config.EMAIL_USER, password=config.EMAIL_PWD, host=config.EMAIL_HOST)
            yag.send(
                # to 收件人，如果一个收件人用字符串，多个收件人用列表即可
                # to=['294062541@qq.com', '247178756@qq.com', 'lijiangtao999@dingtalk.com'],
                to=config.EMAIL_RECIPIENT,
                # cc 抄送，含义和传统抄送一致，使用方法和to 参数一致
                cc=config.EMAIL_CC,
                # subject 邮件主题（也称为标题）
                subject=f"通过率:【{report_dir['correct_rate']}%】" + config.EMAIL_TITLE + title_time,
                # contents 邮件正文
                contents=f"""
                    运行测试用例数量 :{report_dir['all_case']}条,
                    成功    :{report_dir['case_success']}条,
                    失败    :{report_dir['case_fail']}条
                    跳过    :{report_dir['case_skip']}条
                    通过率  :{report_dir['correct_rate']}%
                    执行时间:{report_dir['case_time']}条
                    报告已邮件发送！！详情信息请下载附件文件
                    """,
                # attachments 附件，和收件人一致，如果一个附件用字符串，多个附件用列表
                attachments=[file])
            print('send email ok!!!!')

        finally:
            # 记得关掉链接，避免浪费资源
            yag.close()


if __name__ == '__main__':
    print('发送Email')
    SendEmail().yagmail(my_file)
    print('发送成功')
