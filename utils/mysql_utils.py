# -*- coding:utf-8 -*-
"""
@Author: kui
@File:  mysql_utils.py
@CreateTime:  2021-09-30
@desc:  创建pymysql类
"""
import loguru
import pymysql
from dbutils.pooled_db import PooledDB

from common import config

db_host = config.MYSQL_INFO

mylog = loguru.logger


class CreateEngine:
    pool = None

    def __new__(cls, *args, **kwargs):
        # 是否有实例，没用则创建一个实例
        if not hasattr(cls, '_instance'):
            CreateEngine._instance = object.__new__(cls)
            print('CreateEngine实例化')
        return CreateEngine._instance

    def __init__(self, mincached=10, maxcached=20, maxshared=10, maxconnections=200, blocking=True,
                 maxusage=100, setsession=None, reset=True, host=db_host['host'], user=db_host['root'],
                 password=db_host['password'],
                 port=db_host['port'],
                 charset=db_host['charset'], database=db_host['database']):
        """
        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        """
        if not self.pool:
            self.pool = PooledDB(pymysql,
                                 mincached, maxcached,
                                 maxshared, maxconnections, blocking,
                                 maxusage, setsession, reset,
                                 host=host, port=port, db=database,
                                 user=user, passwd=password,
                                 charset=charset,
                                 cursorclass=pymysql.cursors.DictCursor
                                 )

    def _get_conn(self):
        """
        连接池返回一个连接
        :return: conn 连接属性
        """
        conn = self.pool.connection()
        return conn

    @staticmethod
    def cursor_sql(sql, *args):
        """
        执行sql cursor_sql(),查询语句
        """
        global conn
        try:
            conn = CreateEngine()._get_conn()
            cursor = conn.cursor()
            cursor.execute(sql, args)
            data = cursor.fetchall()
            mylog.success('=' * 20 + '数据库查询成功' + '=' * 20)
        except Exception as e:
            mylog.error('=' * 20 + '未连接数据库或sql语法错误' + '=' * 20)
            raise e
        return data

    @staticmethod
    def insert_sql(sql, list):
        """
        执行sql insert_sql()，插入语句
        """
        global conn
        try:
            conn = CreateEngine()._get_conn()
            cursor = conn.cursor()
            cursor.execute(sql, list)
            conn.commit()
            mylog.success('-' * 50 + '插入成功' + '-' * 50)
        except Exception as e:
            mylog.error('=' * 20 + '未连接数据库或sql语法错误' + '=' * 20)
            raise e

    @staticmethod
    def update_sql(sql):
        """
        执行sql insert_sql()，插入语句
        """
        global conn
        try:
            conn = CreateEngine()._get_conn()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            mylog.success('-' * 50 + '更新成功' + '-' * 50)
        except Exception as e:
            mylog.error('=' * 20 + '未连接数据库或sql语法错误' + '=' * 20)
            raise e

    def __del__(self):
        print('del')
        try:
            conn.close()
            print('数据库已关闭！！！')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    ...
