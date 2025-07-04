import logging
import subprocess
import sys
from pathlib import Path

import allure
import pytest
from loguru import logger
import os
from dotenv import load_dotenv
import re
from datetime import datetime

from common.get_token import write_token_to_yml
from common.get_token_bussiness import write_bussiness_token_to_yml

# 加载环境变量
load_dotenv(".env")


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    """setup and teardown each task"""
    write_token_to_yml()
    write_bussiness_token_to_yml()

    yield

    logger.debug("teardown task fixture")


# Define the CLI command for MidScene.
MIDSCENE_COMMAND = "midscene"


def pytest_collection_modifyitems(items):
    """打印所有收集到的测试项"""
    for item in items:
        logger.info(f"Collected test: {item.nodeid}")
        logger.info(f"Location: {item.location}")


def pytest_sessionstart(session):
    print(f"\nPytest rootdir: {session.config.rootdir}")
    print(f"Current working directory: {Path.cwd()}")


def pytest_configure(config):
    """确保所有路径都基于项目根目录，兼容hrp的用例"""
    os.environ["PROJECT_ROOT"] = str(Path(__file__).parent)

    # Store MidScene options in environment variables for later use
    os.environ["MIDSCENE_HEADED"] = str(config.getoption("--midscene-headed", False))
    os.environ["MIDSCENE_KEEP_WINDOW"] = str(config.getoption("--midscene-keep-window", False))

    allure_dir = config.getoption("--alluredir")
    if allure_dir:
        # 确保目录存在
        allure_dir_path = Path(allure_dir)
        allure_dir_path.mkdir(parents=True, exist_ok=True)

        # 创建环境属性文件
        allure_env_path = allure_dir_path / "environment.properties"
        with open(allure_env_path, 'w') as f:
            f.write(f"UI_Framework=MidScene\n")
            f.write(f"API_Framework=HttpRunner\n")
            f.write(f"Python_Version={sys.version.split()[0]}\n")
            f.write(f"MidScene_Command={MIDSCENE_COMMAND}\n")
            f.write(f"Execution_Time={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def pytest_collect_file(parent, file_path):
    """Pytest hook to discover MidScene YAML files"""
    if (file_path.suffix == ".yml" or file_path.suffix == ".yaml") and "UI" in file_path.parts:
        return MidSceneFile.from_parent(parent, path=file_path)
    return None


def pytest_addoption(parser):
    """Add MidScene-specific command line options"""
    parser.addoption("--midscene-headed", action="store_true", help="Run MidScene in headed mode")
    parser.addoption("--midscene-keep-window", action="store_true", help="Keep browser window open after test")


class MidSceneFile(pytest.File):
    """A custom pytest File collector for MidScene YAML files"""

    def collect(self):
        yield MidSceneItem.from_parent(self, name=self.path.stem)


class MidSceneItem(pytest.Item):
    """A custom pytest Item that runs a MidScene test"""

    def __init__(self, *, parent, name, **kwargs):
        super().__init__(name=name, parent=parent, **kwargs)
        self._obj = lambda: None
        self._obj.__doc__ = f"MidScene test from {self.path}"
        self.midscene_report_path = None

    def runtest(self):
        """Executes the test by calling the MidScene CLI as a subprocess"""
        import shutil

        allure.dynamic.title(f"UI Test: {self.name}")
        allure.dynamic.description(f"MidScene UI test from file: {self.path}")
        allure.dynamic.feature("UI Automation")
        allure.dynamic.story(f"UI/{'/'.join(self.path.parts[self.path.parts.index('UI') + 1:])}")

        if not shutil.which(MIDSCENE_COMMAND):
            with allure.step("检查MidScene可用性"):
                allure.attach(f"'{MIDSCENE_COMMAND}' not found in PATH", "错误", allure.attachment_type.TEXT)
            pytest.fail(f"'{MIDSCENE_COMMAND}' not found in PATH. Is it installed?", pytrace=False)

        if not self.path.exists():
            with allure.step("检查测试文件"):
                allure.attach(f"Test file not found: {self.path}", "错误", allure.attachment_type.TEXT)
            pytest.fail(f"Test file not found: {self.path}", pytrace=False)

        project_root = Path(__file__).parent.parent
        midscene_report_dir = project_root / "midscene_run" / "report"
        midscene_report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        command = [
            MIDSCENE_COMMAND,
            str(self.path.resolve()),
            "--report-dir", str(midscene_report_dir)
        ]

        # Add optional parameters based on pytest command line options
        if os.environ.get("MIDSCENE_HEADED", "False") == "True":
            command.append("--headed")

        if os.environ.get("MIDSCENE_KEEP_WINDOW", "False") == "True":
            command.append("--keep-window")

        with allure.step(f"执行MidScene命令: {' '.join(command)}"):
            allure.attach(f"运行目录: {project_root}", "信息", allure.attachment_type.TEXT)
            logger.info(f"Running in: {project_root}")
            logger.info(f"Executing: {' '.join(command)}")

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    shell=True,
                    cwd=str(project_root),
                    timeout=300,
                )

                if result.stdout:
                    allure.attach(result.stdout, "标准输出", allure.attachment_type.TEXT)
                if result.stderr:
                    allure.attach(result.stderr, "标准错误", allure.attachment_type.TEXT)

                report_pattern = re.compile(rf"{self.name}-\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}}-\w+\.html")
                latest_report = None
                latest_time = 0

                for file in midscene_report_dir.glob("*.html"):
                    if report_pattern.match(file.name):
                        file_time = file.stat().st_mtime
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_report = file

                if latest_report:
                    self.midscene_report_path = latest_report
                    logger.info(f"找到MidScene报告: {latest_report}")

                    allure_results_dir = Path(self.config.getoption("--alluredir"))
                    if allure_results_dir.exists():
                        report_copy_path = allure_results_dir / f"midscene_{self.name}_{timestamp}.html"
                        shutil.copy2(latest_report, report_copy_path)
                        logger.info(f"复制报告到Allure目录: {report_copy_path}")

                    with open(latest_report, 'r', encoding='utf-8') as f:
                        report_content = f.read()

                    allure.attach(
                        report_content,
                        f"MidScene HTML报告 ({latest_report.name})",
                        allure.attachment_type.HTML
                    )

                    allure.attach(
                        f"报告路径: {latest_report}\n"
                        f"可以通过以下方式查看完整报告:\n"
                        f"1. 在Allure报告中点击上方的HTML附件\n"
                        f"2. 直接打开文件: {latest_report}",
                        "报告位置",
                        allure.attachment_type.TEXT
                    )
                else:
                    logger.warning("未找到MidScene报告文件")
                    allure.attach(
                        "未找到MidScene生成的HTML报告文件",
                        "警告",
                        allure.attachment_type.TEXT
                    )

                if result.returncode != 0:
                    error_msg = f"MidScene failed (code {result.returncode}):\n{result.stderr or result.stdout}"
                    with allure.step("执行失败"):
                        allure.attach(error_msg, "错误详情", allure.attachment_type.TEXT)
                    pytest.fail(error_msg, pytrace=False)
                else:
                    with allure.step("执行成功"):
                        allure.attach("测试通过", "结果", allure.attachment_type.TEXT)

            except subprocess.TimeoutExpired:
                with allure.step("执行超时"):
                    allure.attach("Test timed out after 5 minutes", "错误", allure.attachment_type.TEXT)
                pytest.fail("Test timed out after 5 minutes", pytrace=False)

    def repr_failure(self, excinfo):
        """Custom failure reporting"""
        if hasattr(excinfo, 'errisinstance') and hasattr(pytest, 'fail'):
            if excinfo.errisinstance(pytest.fail.Exception):
                return str(excinfo.value)

        if isinstance(excinfo.value, AssertionError):
            return str(excinfo.value)

        return super().repr_failure(excinfo)

    def reportinfo(self):
        """Returns the test's name and path for reporting"""
        return self.path, 0, f"test: {self.name}"


def pytest_runtest_makereport(item, call):
    """处理测试报告，为UI测试添加额外信息"""
    if isinstance(item, MidSceneItem) and call.when == "call":
        if hasattr(item, 'midscene_report_path') and item.midscene_report_path:
            item.user_properties.append(("midscene_report", str(item.midscene_report_path)))

            if call.excinfo:
                try:
                    with open(item.midscene_report_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    error_match = re.search(r'<div class="error-message">(.*?)</div>', content, re.DOTALL)
                    if error_match:
                        error_info = error_match.group(1).strip()
                        allure.attach(
                            error_info,
                            "MidScene错误详情",
                            allure.attachment_type.TEXT
                        )
                except Exception as e:
                    logger.error(f"提取MidScene错误信息失败: {e}")
