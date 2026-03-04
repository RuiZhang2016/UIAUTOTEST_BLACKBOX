"""
Pytest 全局配置文件
定义 fixtures（浏览器页面、失败截图）和 Allure 环境配置。
"""
import os
import sys
import platform
from pathlib import Path

import pytest
import allure
from dotenv import load_dotenv

from utils.log_utils import logs
from utils.settings import FILE_PATH

PROJECT_ROOT_PATH = FILE_PATH["PROJECT_ROOT_PATH"]

# 根据 ENV 环境变量加载对应的 .env 配置文件
env_test = os.getenv("ENV", "pre")
env_path = os.path.join(PROJECT_ROOT_PATH, f".env.{env_test}.toml")

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

if not os.path.exists(FILE_PATH["allure"]):
    os.makedirs(FILE_PATH["allure"])


# ══════════════════ Pytest Hooks ══════════════════

def pytest_sessionstart(session):
    """测试会话开始时写入 Allure 环境信息文件"""
    project = Path(PROJECT_ROOT_PATH).name
    envi = os.getenv("ENV", "pre")

    Path("allure_results").mkdir(exist_ok=True)
    env_file = Path("allure_results/environment.properties")
    with env_file.open("w", encoding="utf-8") as f:
        f.write(f"Project={project}\n")
        f.write(f"Environment={envi}\n")
        f.write(f"OS_Version={platform.platform()}\n")
        f.write(f"Python_Version={sys.version.split()[0]}\n")
        f.write(f"Machine={platform.machine()}\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """捕获每个测试的执行结果，供 screenshot_on_failure fixture 使用"""
    outcome = yield
    result = outcome.get_result()
    setattr(item, "rep_" + result.when, result)


# ══════════════════ Fixtures ══════════════════

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="function", autouse=False)
def page(browser, request):
    """创建浏览器页面，带默认 20 秒超时，测试结束后自动关闭"""
    try:
        logs.info(f"使用设备为 {os.getenv('device')}")
        context = browser.new_context(permissions=["geolocation"])
        context.set_default_timeout(20000)
        page = context.new_page()
        yield page
    finally:
        page.close()
        context.close()


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, page):
    """测试失败时自动截图并附加到 Allure 报告"""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"失败截图 - {request.node.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            logs.warning(f"截图失败: {e}")
