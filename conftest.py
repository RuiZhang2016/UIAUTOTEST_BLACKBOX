"""
Global pytest configuration.
Defines fixtures (browser page, failure screenshots) and Allure environment setup.
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

# Load the .env config file corresponding to the ENV environment variable
env_test = os.getenv("ENV", "pre")
env_path = os.path.join(PROJECT_ROOT_PATH, f".env.{env_test}.toml")

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

if not os.path.exists(FILE_PATH["allure"]):
    os.makedirs(FILE_PATH["allure"])


# ══════════════════ Pytest Hooks ══════════════════

def pytest_sessionstart(session):
    """Write Allure environment properties file at the start of the test session."""
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
    """Capture test outcome for each phase, used by the screenshot_on_failure fixture."""
    outcome = yield
    result = outcome.get_result()
    setattr(item, "rep_" + result.when, result)


# ══════════════════ Fixtures ══════════════════

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="function", autouse=False)
def page(browser, request):
    """Create a browser page with a default 20s timeout; auto-closed after the test."""
    try:
        logs.info(f"Using device: {os.getenv('device')}")
        context = browser.new_context(permissions=["geolocation"])
        context.set_default_timeout(20000)
        page = context.new_page()
        yield page
    finally:
        page.close()
        context.close()


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, page):
    """Automatically capture a full-page screenshot on test failure and attach it to Allure."""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"failure_screenshot - {request.node.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            logs.warning(f"Failed to capture screenshot: {e}")
