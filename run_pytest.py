import logging
import multiprocessing
import concurrent.futures

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

    # 补充支持多个case路径
    # case = [r"testcases/api/pp_app/airtime/agent_status_test.py", r"testcases/pp_app"]
    case = [r"testcases/api/pp_app/airtime/agent_status_test.py"]

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


def run_process(target_func, func_name="未命名函数"):
    """运行一个进程并等待其完成，返回是否成功"""
    process = multiprocessing.Process(target=target_func)
    try:
        logging.info(f"开始执行{func_name}")
        process.start()
        process.join()
        
        if process.exitcode == 0:
            logging.info(f"{func_name}执行成功")
            return True
        else:
            logging.error(f"{func_name}执行失败，退出码: {process.exitcode}")
            return False
    except Exception as e:
        logging.error(f"{func_name}执行异常: {e}")
        return False
    finally:
        # 确保进程被终止
        if process.is_alive():
            process.terminate()
            process.join(timeout=3)
            if process.is_alive():
                process.kill()


def run_sequential_tasks():
    """按顺序执行多个任务，确保前一个任务成功后再执行下一个"""
    with multiprocessing.Pool(processes=1) as pool:
        # 执行报告生成
        report_result = pool.apply(allure_report)
        if not report_result:
            logging.error("报告生成失败，终止后续任务")
            return False
            
        # 执行钉钉消息发送
        # msg_result = pool.apply(send_ding_msg)
        # if not msg_result:
        #     logging.error("钉钉消息发送失败")
        #     return False
            
        return True

def send_ding_allure_report_main():
    """使用concurrent.futures执行报告生成和消息发送"""
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        try:
            # 提交报告生成任务
            future = executor.submit(allure_report)
            # 等待报告生成完成
            result = future.result()  # 如果allure_report有返回值，可以检查结果
            
            # 如果需要发送钉钉消息，取消下面的注释
            # future = executor.submit(send_ding_msg)
            # result = future.result()
            
            return True
        except Exception as e:
            logging.error(f"执行任务时发生异常: {e}")
            return False


def run_main():
    # 1. 跑用例之前，调用自动化平台造数接口api,实现自动化数据统计
    # call_ms_api()

    # 2. 报告归档当日日期的目录下
    send_ding_allure_report_main()

    # 3. 上传allure报告到服务器
    upload_report()


if __name__ == "__main__":
    run_main()
