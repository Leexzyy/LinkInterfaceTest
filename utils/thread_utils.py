# -*- coding: utf-8 -*-
# @Time    : 2023/12/28 18:34
# @Author  : Leexzyy
# @Site    : 
# @File    : thread_utils.py.py
# @Software: PyCharm
import concurrent.futures
import threading
import time


def thread_test(func, json=None, nuber_of_thread=2):
    result_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=nuber_of_thread) as executor:
        for i in range(nuber_of_thread):
            future = executor.submit(func, json)
            result = future.result()
            result_list.append(result)
            print(time.time())
    return result_list


def thread_test_2(func):
    def run_func(func, json, nuber_of_thread):
        result_list = []
        threads = []
        for i in range(nuber_of_thread):
            thread = threading.Thread(target=func, args=(json, nuber_of_thread)).start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    return run_func


if __name__ == '__main__':
    pass
#     @thread_test_2
#     def test_func(json):
#         return json
#
# test.py = thread_test(json={'test.py'}, nuber_of_thread=3)
# print(test.py)
