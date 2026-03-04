"""
项目路径配置模块
定义项目根目录和各关键目录的路径映射，供全局使用。
"""
import os
import sys

PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT_PATH)

FILE_PATH = {
    "PROJECT_ROOT_PATH": PROJECT_ROOT_PATH,
    "allure": os.path.join(PROJECT_ROOT_PATH, "allure_results"),
    "log": os.path.join(PROJECT_ROOT_PATH, 'log'),
    "image": os.path.join(PROJECT_ROOT_PATH, 'image'),
}
