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

        # Build command as a list first
        command_parts = [
            MIDSCENE_COMMAND,
            str(self.path.resolve())
        ]

        # Add optional parameters based on pytest command line options
        if os.environ.get("MIDSCENE_HEADED", "False") == "True":
            command_parts.append("--headed")

        if os.environ.get("MIDSCENE_KEEP_WINDOW", "False") == "True":
            command_parts.append("--keep-window")

        # Convert to string for shell execution
        command = " ".join(command_parts)

        with allure.step(f"执行MidScene命令: {command}"):
            allure.attach(f"运行目录: {project_root}", "信息", allure.attachment_type.TEXT)
            logger.info(f"Running in: {project_root}")
            logger.info(f"Executing: {command}")

            try:
                # Use Popen for real-time output and better process control
                import time
                from threading import Thread
                import queue

                def read_output(pipe, q, prefix=""):
                    """Read output from pipe and put into queue"""
                    try:
                        for line in iter(pipe.readline, ''):
                            if line:
                                q.put((prefix, line.rstrip()))
                        pipe.close()
                    except Exception as e:
                        q.put((prefix, f"Error reading output: {e}"))

                # Start the process
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True,
                    cwd=str(project_root),
                    bufsize=1,
                    universal_newlines=True
                )

                # Create queues for output
                output_queue = queue.Queue()

                # Start threads to read stdout and stderr
                stdout_thread = Thread(target=read_output, args=(process.stdout, output_queue, "STDOUT"))
                stderr_thread = Thread(target=read_output, args=(process.stderr, output_queue, "STDERR"))

                stdout_thread.daemon = True
                stderr_thread.daemon = True
                stdout_thread.start()
                stderr_thread.start()

                # Collect output and monitor process
                all_stdout = []
                all_stderr = []
                start_time = time.time()
                timeout_seconds = 300  # 5 minutes should be enough for UI tests
                execution_completed = False

                logger.info("MidScene execution started, monitoring output...")

                while True:
                    # Check if process has finished
                    if process.poll() is not None:
                        logger.info(f"MidScene process finished with return code: {process.returncode}")
                        break

                    # Check for timeout
                    if time.time() - start_time > timeout_seconds:
                        if execution_completed:
                            logger.info("MidScene execution completed but process still running (likely due to --keep-window), terminating gracefully")
                            try:
                                process.terminate()
                                process.wait(timeout=10)
                            except:
                                process.kill()
                            break
                        else:
                            logger.error(f"MidScene process timeout after {timeout_seconds} seconds without completion signal")
                            try:
                                process.terminate()
                                process.wait(timeout=10)
                            except:
                                process.kill()
                            raise subprocess.TimeoutExpired(command, timeout_seconds)

                    # Read and display output
                    try:
                        while True:
                            prefix, line = output_queue.get_nowait()
                            if prefix == "STDOUT":
                                all_stdout.append(line)
                                logger.info(f"MidScene: {line}")

                                # Check for execution completion signals
                                if "Execution Summary:" in line:
                                    logger.info("Detected MidScene execution summary - test execution completed")
                                    execution_completed = True
                                elif execution_completed and ("🎉 All files executed successfully!" in line or
                                                            "❌ Some files failed to execute" in line or
                                                            "⚠️ Some files were not executed" in line):
                                    logger.info("MidScene execution fully completed, will terminate process after brief delay")
                                    # Give a small delay to ensure all output is captured
                                    time.sleep(2)
                                    try:
                                        process.terminate()
                                        process.wait(timeout=10)
                                    except:
                                        process.kill()
                                    break

                            else:  # STDERR
                                all_stderr.append(line)
                                logger.warning(f"MidScene Error: {line}")
                    except queue.Empty:
                        pass

                    time.sleep(0.1)  # Small delay to prevent busy waiting

                # Collect any remaining output
                try:
                    while True:
                        prefix, line = output_queue.get_nowait()
                        if prefix == "STDOUT":
                            all_stdout.append(line)
                        else:
                            all_stderr.append(line)
                except queue.Empty:
                    pass

                # Wait for threads to finish
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)

                # Create a result-like object
                class ProcessResult:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = '\n'.join(stdout)
                        self.stderr = '\n'.join(stderr)

                result = ProcessResult(
                    process.returncode if process.returncode is not None else 0,
                    all_stdout,
                    all_stderr
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

            except subprocess.TimeoutExpired as e:
                # This should rarely happen now since we handle timeout in the main loop
                with allure.step("执行超时"):
                    allure.attach(f"MidScene process timed out: {str(e)}", "错误", allure.attachment_type.TEXT)
                pytest.fail(f"MidScene process timed out: {str(e)}", pytrace=False)
            except Exception as e:
                with allure.step("执行异常"):
                    allure.attach(f"Unexpected error: {str(e)}", "错误", allure.attachment_type.TEXT)
                pytest.fail(f"Unexpected error during MidScene execution: {str(e)}", pytrace=False)

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
