import pytest
import os

from common.ms_auto_statistics import MeterSphere

if __name__ == "__main__":
    # 跑用例之前，调用自动化平台造数接口api,实现自动化数据统计
    # ms = MeterSphere()
    # ms.post_factory_api()

    pytest.main(['-s', '-v', r'.\testcases\Bussiness\data\data_records_latest_test.py', '--alluredir', 'allure_result', "--clean-alluredir"])
    os.system(r"allure generate .\allure_result\ -o .\allure_report\ --clean")
