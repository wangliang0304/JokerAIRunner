import logging
import os
from typing import Text

from util.time_util import get_today_date


def root_path():
    """ 获取 根路径 """
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def ensure_path_sep(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return root_path() + path


def get_config_path(name="config.yml"):
    # root_path + config + config.yml 三个路径拼接
    return os.path.join(root_path(), "config", name)


def get_token_path(name="token.yml"):
    """获取C端token文件路径"""
    # 如果文件不存在，则创建文件
    if not os.path.exists(os.path.join(root_path(), name)):
        with open(os.path.join(root_path(), name), "w") as f:
            f.write("token: \n")
    return os.path.join(root_path(), name)

def get_token_path_bussiness(name="token_bussiness.yml"):
    """获取C端token文件路径"""
    # 如果文件不存在，则创建文件
    if not os.path.exists(os.path.join(root_path(), name)):
        with open(os.path.join(root_path(), name), "w") as f:
            f.write("token: \n")
    return os.path.join(root_path(), name)


def get_allure_html_report_path():
    # 获取allure结果路径：allure_report
    try:
        allure_report_path = os.path.join(root_path(), "allure_report")
        return allure_report_path
    except Exception as e:
        logging.error(f"获取Allure报告路径失败：{e}")


def get_allure_result_path():
    # 获取allure结果路径：allure_result
    try:
        allure_result_path = os.path.join(root_path(), "allure_result")
        return allure_result_path
    except Exception as e:
        logging.error(f"获取Allure结果路径失败：{e}")


def get_allure_report_summary_path():
    # 获取allure结果路径：allure_report/{20240415}/widgets/summary.json
    # 获取当前日期字符串时间
    today_str = get_today_date()
    try:
        allure_report_path = os.path.join(root_path(), "allure_report", today_str, "widgets", "summary.json")
        logging.debug("获取Allure报告摘要路径成功")
        return allure_report_path
    except Exception as e:
        logging.error(f"获取Allure报告摘要路径失败：{e}")


if __name__ == '__main__':
    # print(get_config_path("config.yml"))
    get_allure_report_summary_path()
