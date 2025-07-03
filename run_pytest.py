import logging
import multiprocessing

import pytest
import os

from common.ms_auto_statistics import MeterSphere
from config.server_config import REMOTE_SERVER_URL, USER_NAME, PASSWORD, REMOTE_PATH
from util.ding_util import send_ding_msg
from util.file_util import FileUtils
from util.path_util import get_allure_html_report_path, get_allure_result_path
from util.sftp_util import SftpUploader
from util.time_util import get_today_date


def call_ms_api():
    """
    调用自动化平台api，实现自动化数据统计
    :return:
    """
    ms = MeterSphere()
    ms.post_factory_api()


def upload_report():
    """
    上传allure报告到服务器
    :return:
    """
    hostname = REMOTE_SERVER_URL
    port = 22
    username = USER_NAME
    password = PASSWORD
    local_dir = get_allure_html_report_path()
    remote_dir = REMOTE_PATH

    # 创建 SftpUploader 实例并上传文件
    uploader = SftpUploader(hostname, port, username, password)
    uploader.connect()
    uploader.create_remote_dir_structure(local_dir, remote_dir)
    uploader.disconnect()


def allure_report():
    """
    生成allure报告
    :return:
    """
    today_str = get_today_date()
    result_root = get_allure_result_path()
    report_root = get_allure_html_report_path()
    allure_result = os.path.join(result_root, today_str)
    allure_report = os.path.join(report_root, today_str)

    # case = ".\\testcases\pp_app\data"
    # 补充支持多个case路径
    # case = [r"testcases/Bussiness/data/data_itemlist_test.py", r"testcases/Bussiness/data/data_menulist_test.py"]
    case = [r"testcases/Bussiness", r"testcases/pp_app"]
    # case = [r"testcases/pp_app"]

    # 删除冗余的allure结果和allure report报告
    fileUtilTool = FileUtils()
    fileUtilTool.remove_dir(result_root)
    logging.info("清理历史测试结果")
    fileUtilTool.remove_dir(report_root)
    logging.info("清理历史测试报告")

    # 执行运营用例的pytest命令
    pytest.main(
        ['-s', '-v'] + case + ['--alluredir', allure_result, "--clean-alluredir"])  # case以List方式拼接不同用例集合
    os.system(rf"allure generate {allure_result} -o {allure_report} --clean")


def send_ding_allure_report_main():
    # 根据当日的最新allure报告发送钉钉消息
    # 保证报告生成后，才发送邮件
    a = multiprocessing.Process(target=allure_report)
    # b = multiprocessing.Process(target=send_ding_msg)

    a.start()
    a.join()  # 等待 allure_report 执行完毕
    # b.start()
    # b.join()  # 等待 send_ding_msg 执行完毕


def run_main():
    # 1. 跑用例之前，调用自动化平台造数接口api,实现自动化数据统计
    # call_ms_api()

    # 2. 报告归档当日日期的目录下
    send_ding_allure_report_main()

    # 3. 上传allure报告到服务器
    upload_report()


if __name__ == "__main__":
    run_main()
