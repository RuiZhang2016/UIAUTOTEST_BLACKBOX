"""
Shared BDD step definitions module.
Provides common utilities such as screenshot comparison, and re-exports
frequently used pytest-bdd symbols for wildcard import by test modules.
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
    Perform a pixel-level comparison between the current screenshot and a baseline image.
    Returns the diff rate. On the first run the baseline is saved automatically.
    When the diff exceeds the threshold, comparison images are attached to the Allure report.
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
