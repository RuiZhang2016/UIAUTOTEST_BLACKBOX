"""
BDD 公共步骤定义模块
提供截图对比等通用工具函数，以及 pytest-bdd 常用符号的统一导出，
供各测试模块通过 wildcard import 使用。
"""
import io
import os
import time

import allure
import pytest
from pytest_bdd import given, when, then, parsers
from PIL import Image, ImageChops

from utils.common import *
from utils.settings import FILE_PATH


def compare_screenshot(baseline_name: str, screenshot: bytes, threshold: float = 0.05) -> float:
    """
    将当前截图与基线图片做像素级对比，返回差异率。
    首次运行时自动保存基线；差异超过阈值时将对比图附加到 Allure 报告。
    """
    baseline_dir = os.path.join(FILE_PATH["image"], "baseline")
    diff_dir = os.path.join(FILE_PATH["image"], "diff")
    os.makedirs(baseline_dir, exist_ok=True)
    os.makedirs(diff_dir, exist_ok=True)

    baseline_path = os.path.join(baseline_dir, baseline_name)
    diff_path = os.path.join(diff_dir, baseline_name)

    current_img = Image.open(io.BytesIO(screenshot)).convert("RGB")

    if not os.path.exists(baseline_path):
        current_img.save(baseline_path)
        return 0.0

    baseline_img = Image.open(baseline_path).convert("RGB")
    if current_img.size != baseline_img.size:
        current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

    diff_img = ImageChops.difference(baseline_img, current_img)
    diff_pixels = sum(1 for px in diff_img.getdata() if any(c > 10 for c in px))
    total_pixels = baseline_img.width * baseline_img.height
    diff_rate = diff_pixels / total_pixels

    diff_img.save(diff_path)

    if diff_rate > threshold:
        with open(diff_path, "rb") as f:
            allure.attach(f.read(), name=f"diff_{baseline_name}",
                          attachment_type=allure.attachment_type.PNG)
        with open(baseline_path, "rb") as f:
            allure.attach(f.read(), name=f"baseline_{baseline_name}",
                          attachment_type=allure.attachment_type.PNG)
        allure.attach(screenshot, name=f"current_{baseline_name}",
                      attachment_type=allure.attachment_type.PNG)

    return diff_rate
