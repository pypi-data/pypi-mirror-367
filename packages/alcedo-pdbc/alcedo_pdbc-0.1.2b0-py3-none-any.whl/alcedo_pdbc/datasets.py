# -*- encoding：utf-8 -*-

# ailab.pydc.datasets
# Created :2024-8-10  9:33
# Author：AI Lab 100 Morgan
# Copyright (C) 2020-2024  数智教育发展 (山东) 有限公司
# For license information, see LICENSE.txt
# ID: datasets.py


"""
#

"""

__author__ = 'ailab100-acu'

import json
from typing import Any,Dict,Literal,Union

import connectorx as cx
import pandas as pd
import redis
from  datetime import  datetime,date
from . import mysql_operate
from .config import *
# from .utils import deprecated


class DateToJson(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime):
            return obj.strftime('%Y年%m月%d日 %H:%M:%S')
        elif isinstance(obj,date):
            return obj.strftime('%Y年%m月%d日')
        elif isinstance(obj,'日期'):
            return obj.strftime('%Y年%m月%d日')
        else:
            return json.JSONEncoder.default()


# 定义datasource字典的类型提示
DatasourceDict = Dict[str,Union[str,int]]


# @deprecated(' `ailab.datasets` 方法将在新版本(v1.1.0)中被移除,可使用`ailab.pydc.sql`替代.')
class Dataset:

    @staticmethod
    def read_sql_query(
            query: Union[str,None] = None,
            db: Literal["mysql","postgresql","mssql","oracle","sqlite"] = "mysql",
            datasource: DatasourceDict = None,
            table: Union[str,None] = None,
            partition_on: Union[str,None] = None,
            partition_num: Union[int,None] = None,
            return_type: Literal["pandas"] = "pandas"
    ) -> Union[pd.DataFrame,Any]:
        """
        根据query,table和datasource获取数据到dataframe,当datasource为空时,默认数据源为ailab数据库;当query为空时,系统优先从redis获取数据.

        :param query: str,默认值为空,从table表中获取全部记录;query和table两个参数不允许同时为空
        :param datasource: str,默认值为空,取默认数据源
        :param table: str,默认值为空,根据query返回查询记录;query和table两个参数不允许同时为空
        :return:
        """

        # 根据db_type确定datasource需要的键
        # if db == "sqlite":
        #     required_keys = {'DB_PATH'}  # 或者 {'database'} 如果你愿意这样命名
        # else:
        #     required_keys = {'HOST','USERNAME','PASSWORD','PORT','DATABASE'}

        # # 验证datasource是否包含所有必要的键
        # if not required_keys.issubset(datasource.keys()):
        #     missing_keys = required_keys - set(datasource.keys())
        #     raise ValueError(f"datasource must contain {', '.join(missing_keys)}")

        # 建立redis连接
        redis_conn = redis.Redis(host=DATALAKE_REDIS_HOST,
                                 port=DATALAKE_REDIS_PORT,
                                 db=DATALAKE_REDIS_DB,
                                 password=DATALAKE_REDIS_PASSWORD
                                 )

        if datasource is None:
            # 创建或获取数据源连接
            conn_str = f'mysql://{DATALAKE_MYSQL_USER}:{DATALAKE_MYSQL_PASSWD}@{DATALAKE_MYSQL_HOST}:{DATALAKE_MYSQL_PORT}/{DATALAKE_MYSQL_DB}'
        elif db == "sqlite":
            conn_str = 'sqlite://' + datasource['DB_PATH']
        else:
            conn_engine = f"{db}://{datasource['USERNAME']}:{datasource['PASSWORD']}@{datasource['HOST']}:{datasource['PORT']}"
            if 'DATABASE' in datasource:
                if datasource['DATABASE']:
                    dbname_in_config = True
                    conn_str = f"{conn_engine}/{datasource['DATABASE']}"
        print(conn_str)
        # 检查参数并设置默认SQL查询（如果必要）

        if query is None and table is not None:
            cache_key = DATALAKE_REDIS_CACHE_PREFIX + table
            # 尝试从Redis获取数据
            cached_value = redis_conn.get(cache_key)
            if cached_value is not None:
                return pd.DataFrame(json.loads(cached_value.decode('utf-8')))
            else:
                query = f"SELECT * FROM {table}"
                df = cx.read_sql(conn=conn_str,
                                 query=query,
                                 partition_on=partition_on,
                                 partition_num=partition_num,
                                 return_type=return_type
                                 )
                redis_conn.set(cache_key,
                               df.to_json(orient='records'),
                               ex=DATALAKE_REDIS_EXPIRE_TIME
                               )
                return df

        elif query is not None:

            cache_key = query.replace(" ","_")
            cached_value = redis_conn.get(cache_key)
            if cached_value is not None:
                return pd.DataFrame(json.loads(cached_value.decode('utf-8')))
            else:
                df = cx.read_sql(conn=conn_str,
                                 query=query,
                                 partition_on=partition_on,
                                 partition_num=partition_num,
                                 return_type=return_type
                                 )
                redis_conn.set(cache_key,
                               df.to_json(orient='records'),
                               ex=3600
                               )

                return df
        else:
            raise ValueError("参数query和table不允许同时为空")

    @staticmethod
    def read_sql_table(table):
        """获取所有用户信息"""
        redis_conn = redis.Redis(
            host=DATALAKE_REDIS_HOST,
            port=DATALAKE_REDIS_PORT,
            db=DATALAKE_REDIS_DB,
            password=DATALAKE_REDIS_PASSWORD
        )
        cache_key = DATALAKE_REDIS_CACHE_PREFIX + table
        # 尝试从Redis获取数据
        cached_value = redis_conn.get(cache_key)
        if cached_value is not None:
            return pd.DataFrame(json.loads(cached_value.decode('utf-8')))
        else:
            sql = "SELECT * FROM {table_name}"  # sql语句，可自行对应自己数据相应的表进行操作
            sql = sql.format(table_name=table)
            data = mysql_operate.Conn.select_db(sql)  # 用mysql_operate文件中的Conn的select_db方法进行查询
            # 将数据保存到Redis中
            try:
                redis_conn.set(cache_key,
                               json.dumps(data),
                               ex=DATALAKE_REDIS_EXPIRE_TIME
                               )
            except Exception as e:
                pass
            return pd.DataFrame(data)  # 在页面输出返回信息的dataframe格式
