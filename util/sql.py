import os

import yaml
from sqlalchemy.dialects.mysql import pymysql


def connect_database(filepath, sql):
    if os.path.exists(filepath):
        config_data = open(filepath, 'r', encoding='utf-8')
        res = yaml.load(config_data, Loader=yaml.FullLoader)
    else:
        raise FileNotFoundError('can`t found File')

    # print(type(res['sql_db']))
    # connection = pymysql.connect(host='api.lemonban.com',user='future',password='123456',database='future')
    try:
        connection = pymysql.connect(**res['sql_db'])
    except Exception as e:
        raise ConnectionError('链接失败')

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()
            result = cursor.fetchone()
            print(result)
            return result
    finally:
        # 关闭数据库
        connection.close()

if __name__ == '__main__':
    connect_database('config.yml', 'SELECT * FROM test')
