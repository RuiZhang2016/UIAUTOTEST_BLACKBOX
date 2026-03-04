"""
BDD test case decorator module.
Provides the bdd_case decorator that parses .feature files, injects
Feature/Scenario info into Allure suite/title, and binds pytest-bdd scenarios.
"""
import ast
import json
import os
import re
import inspect
from functools import wraps

import allure
from pytest_bdd import scenario
from gherkin.parser import Parser

from steps.common import step_recorder
from utils.settings import FILE_PATH

# Tracks the mapping between test files and feature files
path_file_decorator_json: dict = dict()


def parse_feature_title_and_scenario(path, scenario_name):
    """Parse the Feature title and specified Scenario name/description from a .feature file."""
    parser = Parser()
    with open(path, encoding="utf-8") as f:
        content = f.read()
    gherkin_document = parser.parse(content)
    try:
        feature = gherkin_document["feature"]
        feature_title = feature["name"]
    except KeyError:
        raise KeyError(f"Feature name not found in {path}")

    os.environ["scenario_name"] = scenario_name
    set1 = set()
    for child in feature.get("children", []):
        sc = child.get('scenario') or child.get('scenarioOutline')
        if sc:
            if not os.getenv("feature_scenario"):
                os.environ["feature_scenario"] = str({feature_title: [sc.get('name')]})
            else:
                z = os.getenv("feature_scenario")
                feature_os = ast.literal_eval(z)
                set1.add(sc.get('name'))
                feature_os[feature_title] = list(set1)
                try:
                    os.environ["feature_scenario"] = json.dumps(feature_os, ensure_ascii=False)
                except TypeError:
                    raise TypeError(f"Feature scenario not json serializable: {feature_os}")
            if sc.get('name') == scenario_name:
                return feature_title, sc["name"], sc["description"]
    raise ValueError(f"Scenario '{scenario_name}' not found in: {path}")


def bdd_case(program_top_directory_name, feature_path, scenario_name):
    """
    BDD test case decorator.
    Parses the feature file, maps the Feature name to an Allure suite,
    maps the Scenario description/name to an Allure title, and binds the pytest-bdd scenario.
    """
    PROJECT_ROOT_PATH = FILE_PATH["PROJECT_ROOT_PATH"]
    program_directory_path = os.path.join(PROJECT_ROOT_PATH, program_top_directory_name)
    if not os.getenv("current_top_directory_name"):
        os.environ["current_top_directory_name"] = program_top_directory_name

    def wrapper(test_func):
        if program_top_directory_name:
            full_path = os.path.join(program_directory_path, "features", feature_path)
        else:
            full_path = os.path.join(os.path.dirname(__file__), "..", "features", feature_path)
        full_path = os.path.abspath(full_path)

        feature_title, scenario_title, description = parse_feature_title_and_scenario(full_path, scenario_name)
        assert scenario_title, f"Scenario '{scenario_name}' not found in: {full_path}"

        # Record test-file-to-feature mapping and write to config/path_file_decorator.json
        path_file_decorator: str = inspect.getfile(test_func)
        global path_file_decorator_json
        pfd_key = f"{path_file_decorator}::{test_func.__name__}"
        pfd_key = re.sub(r"\\", "/", pfd_key) if re.search(r"\\", pfd_key) else pfd_key

        if not path_file_decorator_json.get(pfd_key):
            path_file_decorator_json[pfd_key] = list()
        pfd_value = f"{full_path}::{scenario_name}"
        pfd_value = re.sub(r"\\", "/", pfd_value) if re.search(r"\\", pfd_value) else pfd_value
        if pfd_value not in path_file_decorator_json[pfd_key]:
            path_file_decorator_json[pfd_key].append(pfd_value)

        config_dir = os.path.join(PROJECT_ROOT_PATH, "config")
        os.makedirs(config_dir, exist_ok=True)
        with open(os.path.join(config_dir, "path_file_decorator.json"),
                  mode="w", encoding="utf-8") as fp:
            json.dump(path_file_decorator_json, fp, allow_nan=True, sort_keys=False)

        @allure.suite(feature_title)
        @allure.title(description if description else scenario_title)
        @scenario(full_path, scenario_name)
        @wraps(test_func)
        @step_recorder(f"scenario {scenario_name} executed")
        def decorated(*args, **kwargs):
            parse_feature_title_and_scenario(full_path, scenario_name)
            return test_func(*args, **kwargs)
        return decorated
    return wrapper
