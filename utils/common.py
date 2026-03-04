"""
通用工具模块
提供 BDD 步骤记录（step_recorder）和步骤追踪（StepTracker）功能，
被 utils/bdd_decorator.py 通过 steps/common.py 间接使用。
"""
import os
from functools import wraps

import allure
from playwright.sync_api import Page

from utils.settings import FILE_PATH


def step_recorder(arg, whether_screen_shot_be_opened=False):
    """
    装饰器：记录 BDD 步骤执行信息到 StepTracker，
    同时在 Allure 报告中创建对应的 step 节点。
    """
    def wrapper1(step_function):
        @wraps(step_function)
        def wrapper(*args, **kwargs):
            step_name = step_function.__name__
            StepTracker().record(step_name, arg, *args, **kwargs)
            with allure.step(arg):
                if type(kwargs.get("page", None)) == Page and whether_screen_shot_be_opened:
                    ps: bytes = kwargs.get("page", None).screenshot(
                        path=os.path.join(FILE_PATH['log'], 'step.jpg'))
                    allure.attach(body=ps, attachment_type=allure.attachment_type.JPG,
                                  name="step main photo")
                return step_function(*args, **kwargs)
        wrapper._is_decorated_by_current_step = True
        return wrapper
    return wrapper1


class StepTracker:
    """跟踪 BDD 步骤执行顺序，通过环境变量传递步骤状态"""
    steps_name_sequence = eval(str(os.getenv("steps_name_sequence")))
    current_step = os.getenv("current_step")
    current_step_args = os.getenv("current_step_args")

    def __init__(self):
        self.current_step = None
        self.params = {}

    def record(self, step_text, arg, *args, **kwargs):
        self.current_step_args = arg
        self.current_step = step_text
        StepTracker.current_step = step_text
        if StepTracker.steps_name_sequence:
            StepTracker.steps_name_sequence.append(step_text)
        else:
            StepTracker.steps_name_sequence = [step_text]
        os.environ["current_step"] = str(step_text)
        os.environ["current_step_args"] = str(arg)
        os.environ["steps_name_sequence"] = str(StepTracker.steps_name_sequence)
        os.environ["current_step_name"] = (
            os.getenv("current_step_args")
            or os.getenv("current_step")
            or os.getenv("scenario_name", "")
        )
