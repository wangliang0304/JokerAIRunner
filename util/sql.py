import os
import logging

import yaml
from sqlalchemy.dialects.mysql import pymysql


def connect_database(filepath, sql):
    if os.path.exists(filepath):
        config_data = open(filepath, 'r', encoding='utf-8')
        res = yaml.load(config_data, Loader=yaml.FullLoader)
    else:
        raise FileNotFoundError('配置文件未找到')

    try:
        connection = pymysql.connect(**res['sql_db'])
        logging.info("数据库连接成功")
    except Exception as e:
        logging.error(f"数据库连接失败：{e}")
        raise ConnectionError('数据库连接失败')

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            result = cursor.fetchone()
            logging.info("SQL执行成功")
            return result
    finally:
        # 关闭数据库
        connection.close()

if __name__ == '__main__':
    connect_database('config.yml', 'SELECT * FROM test')
