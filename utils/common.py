"""
Common utilities module.
Provides BDD step recording (step_recorder) and step tracking (StepTracker),
used by utils/bdd_decorator.py via steps/common.py.
"""
import os
from functools import wraps

import allure
from playwright.sync_api import Page

from utils.settings import FILE_PATH


def step_recorder(arg, whether_screen_shot_be_opened=False):
    """
    Decorator that records BDD step execution info into StepTracker
    and creates a corresponding step node in the Allure report.
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
    """Tracks BDD step execution order and propagates step state via environment variables."""
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
