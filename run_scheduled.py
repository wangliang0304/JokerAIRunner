import os
import pytest
import logging

from run_pytest import run_main, upload_report
from util.file_util import FileUtils
from util.path_util import get_allure_html_report_path, get_allure_result_path
from util.time_util import get_today_date


def run_scheduled(scheduled_job, test_paths=None, run_report=True, upload_report_flag=True):
    """
    Run scheduled job with customized execution options.

    Args:
        scheduled_job: The scheduled job information
        test_paths: Optional list of test paths to run. If None, runs all tests using run_main
        run_report: Whether to generate Allure report
        upload_report_flag: Whether to upload the report to server
    """
    logging.info(f"Running scheduled job: {scheduled_job}")

    if test_paths:
        # Run specific test paths
        logging.info(f"Running specific test paths: {test_paths}")
        today_str = get_today_date()
        result_root = get_allure_result_path()
        report_root = get_allure_html_report_path()
        allure_result = os.path.join(result_root, today_str)
        allure_report_path = os.path.join(report_root, today_str)

        # Clean up previous results if needed
        file_util = FileUtils()
        file_util.remove_dir(result_root)
        logging.info("Removed previous result directory")
        file_util.remove_dir(report_root)
        logging.info("Removed previous report directory")

        # Run pytest with specified paths
        pytest.main(['-s', '-v'] + test_paths + ['--alluredir', allure_result, "--clean-alluredir"])

        # Generate report if requested
        if run_report:
            logging.info("Generating Allure report")
            cmd = rf"allure generate {allure_result} -o {allure_report_path} --clean"
            logging.info(f"Running command: {cmd}")
            exit_code = os.system(cmd)
            if exit_code != 0:
                logging.error(f"Allure report generation failed with exit code {exit_code}")
            else:
                logging.warning("Allure report generated successfully")

        # Upload report if requested
        if upload_report_flag:
            logging.info("Uploading report to server")
            upload_report()
    else:
        # Run all tests using run_main
        logging.info("Running all tests using run_main")
        run_main()
