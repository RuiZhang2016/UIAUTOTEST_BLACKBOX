# UI Auto Test

A Web UI automation testing framework built on **Playwright + pytest-bdd**. It follows the BDD (Behavior-Driven Development) approach — test scenarios are written in Gherkin syntax, validated through pixel-level screenshot comparison for visual regression detection, and reported via Allure.

> [中文文档 (Chinese)](#中文文档)

## Tech Stack

| Category | Tool |
|----------|------|
| Browser Automation | [Playwright](https://playwright.dev/python/) |
| Test Framework | [pytest](https://docs.pytest.org/) + [pytest-bdd](https://pytest-bdd.readthedocs.io/) |
| Test Report | [Allure Report](https://allurereport.org/) |
| Visual Comparison | [Pillow](https://pillow.readthedocs.io/) |
| Logging | [colorlog](https://github.com/borntyping/python-colorlog) + concurrent-safe file rotation |

## Project Structure

```
uiautotest/
├── conftest.py               # Global fixtures & hooks (page management, failure screenshots, Allure env)
├── pytest.ini                # pytest config (markers, addopts, feature paths)
├── requirements.txt          # Python dependencies
├── .env.pre.toml.example     # Environment variable template
│
├── key/                      # Test module
│   ├── features/             #   Gherkin feature files
│   │   └── key_pc_main_page.feature
│   └── steps/                #   Step implementations
│       └── test_key_pc_main_page.py
│
├── steps/                    # Shared steps & utilities
│   └── common.py             #   compare_screenshot + pytest-bdd symbol re-exports
│
├── utils/                    # Core utilities
│   ├── bdd_decorator.py      #   @bdd_case decorator (Feature parsing → Allure suite/title)
│   ├── common.py             #   @step_recorder decorator & StepTracker
│   ├── log_utils.py          #   Colored console + concurrent-safe file logging
│   └── settings.py           #   Project path configuration
│
└── image/
    └── baseline/             # Screenshot baselines (auto-generated on first run)
```

## Key Features

### BDD Test Flow

```
Feature file (Gherkin)  →  @bdd_case decorator  →  Step functions  →  Allure report
```

1. Define test scenarios in Gherkin syntax under `key/features/`
2. Implement corresponding `@when` / `@then` step functions in `key/steps/`
3. The `@bdd_case` decorator automatically binds Feature ↔ Scenario and injects Allure metadata

### Visual Regression Detection

- On the first run, screenshots are automatically saved as baselines (`image/baseline/`)
- Subsequent runs compare current screenshots against baselines at the pixel level; differences exceeding the threshold (default 5%) result in a test failure
- Diff images, baselines, and current screenshots are all automatically attached to the Allure report

### Automatic Failure Screenshots

When a test fails, a full-page screenshot is automatically captured and attached to the Allure report — no manual configuration needed.

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment Variables

```bash
cp .env.pre.toml.example .env.pre.toml
```

Edit `.env.pre.toml` with your actual values:

```toml
device=Desktop Chrome
main_url=https://your-app-url.com
account=your_account
password=your_password
```

### 3. Run Tests

```bash
# Run all tests marked with key_pc
pytest -m key_pc

# Run only P0 priority tests
pytest -m P0

# Run in headless mode (CI environments)
pytest -m key_pc --headless
```

### 4. View Allure Report

```bash
allure serve allure_results
```

## Environment Variables

Managed via `.env.{ENV}.toml` files. `ENV` defaults to `pre`.

| Variable | Description | Example |
|----------|-------------|---------|
| `ENV` | Runtime environment | `pre` / `prod` / `test` |
| `device` | Browser device profile | `Desktop Chrome` |
| `main_url` | URL of the system under test | `https://example.com` |
| `account` | Login account | — |
| `password` | Login password | — |

> `.env.*.toml` is listed in `.gitignore` and will not be committed to the repository.

## Adding New Test Cases

1. **Create a Feature file** — `key/features/your_test.feature`

```gherkin
Feature: your_test

  @P0
  Scenario: your_test
    When open the target page
    Then verify page content
```

2. **Implement step functions** — `key/steps/test_your_test.py`

```python
from steps.common import *
from utils.bdd_decorator import bdd_case

@pytest.mark.key_pc
@bdd_case("key", "your_test.feature", "your_test")
def test_your_case():
    pass

@when("open the target page")
def open_page(page):
    page.goto(os.getenv("main_url"))

@then("verify page content")
def verify(page):
    screenshot = page.screenshot(type="png", full_page=True)
    diff = compare_screenshot("your_baseline.png", screenshot)
    assert diff <= 0.05
```

3. **Run** — `pytest -m key_pc`. Baseline screenshots are auto-generated on the first run.

---

<a id="中文文档"></a>

## 中文文档

基于 **Playwright + pytest-bdd** 的 Web UI 自动化测试框架。采用 BDD 行为驱动开发模式，通过 Gherkin 语法编写测试场景，结合像素级截图对比进行视觉回归检测，并自动生成 Allure 测试报告。

### 技术栈

| 类别 | 工具 |
|------|------|
| 浏览器自动化 | [Playwright](https://playwright.dev/python/) |
| 测试框架 | [pytest](https://docs.pytest.org/) + [pytest-bdd](https://pytest-bdd.readthedocs.io/) |
| 测试报告 | [Allure Report](https://allurereport.org/) |
| 视觉对比 | [Pillow](https://pillow.readthedocs.io/) |
| 日志 | [colorlog](https://github.com/borntyping/python-colorlog) + 并发安全文件轮转 |

### 核心功能

**BDD 测试流程**

```
Feature 文件（Gherkin）  →  @bdd_case 装饰器  →  Step 函数  →  Allure 报告
```

1. 在 `key/features/` 中用 Gherkin 语法定义测试场景
2. 在 `key/steps/` 中实现对应的 `@when` / `@then` 步骤函数
3. `@bdd_case` 装饰器自动绑定 Feature ↔ Scenario，并注入 Allure 元信息

**视觉回归检测**

- 首次运行时自动保存截图为基线（`image/baseline/`）
- 后续运行将当前截图与基线做像素级对比，超过阈值（默认 5%）则判定失败
- 差异图、基线图、当前截图均自动附加到 Allure 报告

**失败自动截图** — 测试失败时自动截取全页截图并附加到 Allure 报告，无需手动配置。

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 2. 配置环境变量
cp .env.pre.toml.example .env.pre.toml
# 编辑 .env.pre.toml 填入实际值

# 3. 运行测试
pytest -m key_pc

# 4. 查看报告
allure serve allure_results
```

### 环境变量

通过 `.env.{ENV}.toml` 文件管理，`ENV` 默认为 `pre`。

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ENV` | 运行环境 | `pre` / `prod` / `test` |
| `device` | 浏览器设备配置 | `Desktop Chrome` |
| `main_url` | 被测系统 URL | `https://example.com` |
| `account` | 登录账号 | — |
| `password` | 登录密码 | — |

> `.env.*.toml` 已加入 `.gitignore`，不会提交到仓库。

---

## License

MIT
